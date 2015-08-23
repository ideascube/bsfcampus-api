import datetime
from slugify import slugify

from flask import url_for
from flask_jwt import current_user, verify_jwt

from MookAPI.core import db
from MookAPI.serialization import JsonSerializer
from MookAPI.sync import SyncableDocumentJsonSerializer, SyncableDocument


class ResourceContentJsonSerializer(JsonSerializer):
    pass


class ResourceContent(ResourceContentJsonSerializer, db.EmbeddedDocument):
    """
    .. _ResourceContent:
    
    An embedded document for the actual content of the Resource_.
    """

    meta = {
        'allow_inheritance': True,
        'abstract': True
    }


class ResourceJsonSerializer(SyncableDocumentJsonSerializer):
    __json_additional__ = ['hierarchy', 'is_validated', 'additional_resources_refs']
    __json_dbref__ = ['title', 'slug', 'resource_content']
    __json_hierarchy_skeleton__ = ['additional_resources']
    __json_rename__ = dict(additional_resources_refs='additional_resources')


class Resource(ResourceJsonSerializer, SyncableDocument):
    """
    .. _Resource:
    
    Any elementary pedagogical resource.
    Contains the metadata and a ResourceContent_ embedded document.
    Resource_ objects are organized by Lesson_ objects, *i.e.* each Resource_ references a parent Lesson_.
    """

    meta = {
        'allow_inheritance': True
    }

    ### PROPERTIES

    is_additional = db.BooleanField(default=False)
    """True if the resource is an additional resource, i.e. has a Resource parent (instead of a Lesson)"""

    title = db.StringField(required=True)
    """The title of the Resource_."""

    slug = db.StringField(unique=True)
    """A human-readable unique identifier for the Resource_."""

    ## Will be implemented later
    # creator = db.ReferenceField('User')
    # """The user who created the resource."""

    description = db.StringField()
    """A text describing the Resource_."""

    order = db.IntField()
    """The order of the Resource_ in the Lesson_."""

    keywords = db.ListField(db.StringField())
    """A list of keywords to index the Resource_."""

    date = db.DateTimeField(default=datetime.datetime.now, required=True)
    """The date the Resource_ was created."""

    parent = db.ReferenceField('Lesson')
    """The parent hierarchy object (usually Lesson, but can be overridden)."""

    parent_resource = db.ReferenceField('Resource')
    """The parent hierarchy object (usually Lesson, but can be overridden)."""

    resource_content = db.EmbeddedDocumentField(ResourceContent)
    """The actual content of the Resource_, stored in a ResourceContent_ embedded document."""

    ### VIRTUAL PROPERTIES

    @property
    def url(self):
        return url_for("resources.get_resource", resource_id=self.id, _external=True)

    def is_validated_by_user(self, user):
        """Whether the current user (if any) has validated this Resource_."""
        from MookAPI.services import completed_resources

        return completed_resources.find(resource=self, user=user).count() > 0

    @property
    def is_validated(self):
        try:
            verify_jwt()
        except:
            pass
        if not current_user:
            return None
        return self.is_validated_by_user(current_user.user)

    @property
    def skill(self):
        """Shorthand virtual property to the parent Skill_ of the parent Lesson_."""
        return self.parent.skill

    @property
    def track(self):
        """Shorthand virtual property to the parent Track_ of the parent Skill_ of the parent Lesson_."""
        return self.parent.skill.track

    @property
    def additional_resources(self):
        """A queryset of the Resources_ objects that are additional resources to the current Resource_."""
        from MookAPI.services import resources

        return resources.find(parent_resource=self).order_by('order', 'title')

    @property
    def additional_resources_refs(self):
        return [additional_resource.to_json_dbref() for additional_resource in self.additional_resources]

    ### METHODS

    def siblings(self):
        """A queryset of Resource_ objects in the same Lesson_, including the current Resource_."""
        return Resource.objects.order_by('order', 'title').filter(parent=self.parent)

    def siblings_strict(self):
        """A queryset of Resource_ objects in the same Lesson_, excluding the current Resource_."""
        return Resource.objects.order_by('order', 'title').filter(parent=self.parent, id__ne=self.id)

    def aunts(self):
        """A queryset of Lesson_ objects in the same Skill_, including the current Lesson_."""
        return self.parent.siblings()

    def aunts_strict(self):
        """A queryset of Lesson_ objects in the same Skill_, excluding the current Lesson_."""
        return self.parent.siblings_strict()

    def cousins(self):
        """A queryset of Resource_ objects in the same Skill_, including the current Resource_."""
        return Resource.objects.order_by('parent', 'order', 'title').filter(parent__in=self.aunts())

    def cousins_strict(self):
        """A queryset of Resource_ objects in the same Skill_, excluding the current Resource_."""
        return Resource.objects.order_by('parent', 'order', 'title').filter(parent__in=self.aunts_strict())

    def _set_slug(self):
        """Sets a slug for the hierarchy level based on the title."""

        slug = self.slug or slugify(self.title)

        def alternate_slug(text, k=1):
            return text if k <= 1 else "{text}-{k}".format(text=text, k=k)

        k = 0
        kmax = 10 ** 4
        while k < kmax:
            if self.id is None:
                req = self.__class__.objects(slug=alternate_slug(slug, k))
            else:
                req = self.__class__.objects(slug=alternate_slug(slug, k), id__ne=self.id)
            if len(req) > 0:
                k = k + 1
                continue
            else:
                break
        self.slug = alternate_slug(slug, k) if k <= kmax else None

    def clean(self):
        super(Resource, self).clean()
        self._set_slug()

    @property
    def bg_color(self):
        return self.track.bg_color

    def user_analytics(self, user):
        from MookAPI.services import visited_resources
        return dict(
            nb_visits=visited_resources.find(user=user, resource=self).count()
        )

    def user_info(self, user, analytics=False):
        info = dict(
            is_validated=self.is_validated_by_user(user)
        )
        if analytics:
            info['analytics'] = self.user_analytics(user)
        return info

    @property
    def hierarchy(self):
        """
        Returns an array of the breadcrumbs up until the current object: [Track_, Skill_, Lesson_, Resource_]
        """
        rv = []

        if self.is_additional:
            rv.extend([
                self.parent_resource.track.to_json_dbref(),
                self.parent_resource.skill.to_json_dbref(),
                self.parent_resource.parent.to_json_dbref(),
                self.parent_resource.to_json_dbref(),
                self.to_json_dbref()
                ]
            )
        else:
            rv.extend([
                self.track.to_json_dbref(),
                self.skill.to_json_dbref(),
                self.parent.to_json_dbref(),
                self.to_json_dbref()
                ]
            )

        return rv

    def __unicode__(self):
        return self.title

    def top_level_syncable_document(self):
        return self.track

    def all_syncable_items(self, local_server=None):
        items = super(Resource, self).all_syncable_items(local_server=local_server)

        for additional_resource in self.additional_resources:
            items.extend(additional_resource.all_syncable_items(local_server=local_server))

        return items
