import datetime
import bson
import slugify

import flask

import MookAPI.mongo_coder as mc
from MookAPI import db, api
import flask.ext.security as security
from .. import views


class ResourceContent(mc.MongoCoderEmbeddedDocument):
    """
    .. _ResourceContent:
    
    An embedded document for the actual content of the Resource_.
    """
    
    meta = {
        'allow_inheritance': True,
        'abstract': True
    }


class Resource(mc.SyncableDocument):
    """
    .. _Resource:
    
    Any elementary pedagogical resource.
    Contains the metadata and a ResourceContent_ embedded document.
    Resource_ objects are organized by Lesson_ objects, *i.e.* each Resource_ references a parent Lesson_.
    """

    meta = {
        'allow_inheritance': True,
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
        return api.url_for(views.ResourceView, resource_id=self.id, _external=True)

    @property
    def is_validated(self):
        """Whether the current user (if any) has validated this Resource_."""
        return self in security.current_user.completed_resources
    
    @classmethod
    def json_key(cls):
        return 'resource'

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

        slug = slugify.slugify(self.title) if self.slug is None else slugify.slugify(self.slug)
        def alternate_slug(text, k=1):
            return text if k <= 1 else "{text}-{k}".format(text=text, k=k)
        k = 0
        kmax = 10**4
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
        self._set_slug()

    def encode_mongo(self):
        son = super(Resource, self).encode_mongo()

        son['breadcrumb'] = self.breadcrumb()
        son['is_validated'] = self.is_validated
        son['bg_color'] = self.track.bg_color

        return son

    def _breadcrumb_item(self):
        """Returns some minimal information about the object for use in a breadcrumb."""

        idkey = self.__class__.json_key() + '_id'
        return {
            'title': self.title,
            'url': self.url,
            'id': self.id,
            idkey: self.id ## Deprecated. Use 'id' instead.
        }

    def breadcrumb(self):
        """
        Returns an array of the breadcrumbs up until the current object: [Track_, Skill_, Lesson_, Resource_]
        """

        return [
            self.track._breadcrumb_item(),
            self.skill._breadcrumb_item(),
            self.parent._breadcrumb_item(),
            self._breadcrumb_item()
        ]
        
    def __unicode__(self):
        return self.title

    @classmethod
    def get_unique_object_or_404(cls, token):
        try:
            oid = bson.ObjectId(token)
        except bson.errors.InvalidId:
            return cls.objects.get_or_404(slug=token)
        else:
            return cls.objects.get_or_404(id=token)

    def top_level_syncable_document(self):
        return self.track
