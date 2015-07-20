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

    def encode_mongo_for_dashboard(self, user):
        response = {'_cls': self._class_name}

        return response


class ResourceJsonSerializer(SyncableDocumentJsonSerializer):
    __json_additional__ = ['breadcrumb', 'is_validated', 'bg_color']
    __json_dbref__ = ['title', 'slug']


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
        user = current_user._get_current_object()
        return self.is_validated_by_user(user)

    @property
    def skill(self):
        """Shorthand virtual property to the parent Skill_ of the parent Lesson_."""
        return self.parent.skill

    @property
    def track(self):
        """Shorthand virtual property to the parent Track_ of the parent Skill_ of the parent Lesson_."""
        return self.parent.skill.track

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

    def encode_mongo_for_dashboard(self, user):
        response = {
            '_id': self._data.get("id", None),
            'is_validated': self.is_validated_by_user(user),
            'title': self.title,
            'order': self.order,
            'resource_content': self.resource_content.encode_mongo_for_dashboard(user)
        }

        from MookAPI.services import visited_resources

        if 'analytics' not in response:
            response['analytics'] = {}
        response['analytics']['nb_visit'] = visited_resources.find(user=user, resource=self).count()

        return response

    @property
    def breadcrumb(self):
        """
        Returns an array of the breadcrumbs up until the current object: [Track_, Skill_, Lesson_, Resource_]
        """

        return [
            self.track.to_json_dbref(),
            self.skill.to_json_dbref(),
            self.parent.to_json_dbref(),
            self.to_json_dbref()
        ]

    def __unicode__(self):
        return self.title

    def top_level_syncable_document(self):
        return self.track
