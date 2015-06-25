import datetime
import bson
import slugify

import MookAPI.mongo_coder as mc
import flask.ext.security as security
from MookAPI import db


class ResourceHierarchy(mc.SyncableDocument):
    """
    .. _ResourceHierarchy:
    
    An abstract class that can describe a Lesson_, a Skill_ or a Track_.
    """

    meta = {
        'allow_inheritance': True,
        'abstract': True
    }

    ### PROPERTIES

    title = db.StringField(required=True)
    """The title of the hierarchy level."""

    slug = db.StringField(unique=True)
    """A human-readable unique identifier for the hierarchy level."""

    description = db.StringField()
    """A text describing the content of the resources in this hierarchy level."""

    order = db.IntField()
    """The order of the hierarchy amongst its siblings."""

    date = db.DateTimeField(default=datetime.datetime.now, required=True)
    """The date the hierarchy level was created."""

    def is_validated(self, user):
        """Whether the user validated the hierarchy level based on their activity."""
        ## Override this method in each subclass
        return False

    def progress(self, user):
        """
        How many sub-units in this level have been validated (current) and how many are there in total (max).
        Returns a dictionary with format: {'current': Int, 'max': Int}
        """
        ## Override this method in each subclass
        return {'current': 0, 'max': 0}
    
    
    ### METHODS

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

    def __unicode__(self):
        return self.title

    @classmethod
    def get_unique_object_or_404(cls, token):
        """Get the only hierarchy level matching argument 'token', where 'token' can be the id or the slug."""

        try:
            bson.ObjectId(token)
        except bson.errors.InvalidId:
            return cls.objects.get_or_404(slug=token)
        else:
            return cls.objects.get_or_404(id=token)

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
        """Returns an array of the breadcrumbs up until the current object."""
        return []

    def encode_mongo(self):
        son = super(ResourceHierarchy, self).encode_mongo()

        son['is_validated'] = self.is_validated(security.current_user)
        son['progress'] = self.progress(security.current_user)
        son['breadcrumb'] = self.breadcrumb()

        return son

    def encode_mongo_for_dashboard(self, user):
        response = {'_id': self._data.get("id", None), 'is_validated': self.is_validated(security.current_user),
                    'progress': self.progress(security.current_user), 'title': self.title, 'order': self.order}

        return response
