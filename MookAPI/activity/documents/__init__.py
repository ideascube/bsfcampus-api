from bson import DBRef
import datetime

from flask import url_for

from MookAPI.core import db
from MookAPI.serialization import CsvSerializer
from MookAPI.sync import SyncableDocumentJsonSerializer, SyncableDocument


class ActivityJsonSerializer(SyncableDocumentJsonSerializer):
    pass


class Activity(ActivityJsonSerializer, CsvSerializer, SyncableDocument):
    """Describes any kind of user activity."""

    meta = {
        'allow_inheritance': True,
        'indexes': [
            '+date',
            'user',
            'type'
        ]
    }

    ### PROPERTIES

    credentials = db.ReferenceField('UserCredentials')
    """The credentials under which the user was logged when they performed the action."""

    user = db.ReferenceField('User')
    """The user performing the activity."""

    user_username = db.StringField(default="")
    """The username (= unique id) of the user who has performed the activity"""

    user_name = db.StringField(default="")
    """The full name of the user who has performed the activity"""
    # FIXME this has to be set using the credentials provided

    date = db.DateTimeField(default=datetime.datetime.now, required=True)
    """The date at which the activity was performed."""

    local_server = db.ReferenceField('LocalServer')
    """The local server on which the activity has been performed"""

    local_server_name = db.StringField()
    """The name of the local server on which the activity has been performed"""

    type = db.StringField()
    """ The type of the activity, so we can group the activities by type to better analyse them.
    This is supposed to be defaulted/initialized in each subclass"""

    @property
    def object(self):
        return None

    object_title = db.StringField()
    """ The title of the object associated to this activity. It allows a better comprehension of the activity than the activity_id.
    This is supposed to be defaulted/initialized in each subclass """

    @property
    def url(self, _external=False):
        print("Activity (%s) url: %s" % (self._cls, self.id))
        return url_for("activity.get_activity", activity_id=self.id, _external=_external)

    @property
    def local_server_id(self):
        return self.local_server.id if self.local_server is not None else ""

    @property
    def user_id(self):
        return self.user.id if self.user is not None else ""

    def clean(self):
        super(Activity, self).clean()
        if self.object and not isinstance(self.object, DBRef):
            self.object_title = getattr(self.object, 'title', None)
        if self.credentials and not isinstance(self.credentials, DBRef):
            self.user = self.credentials.user
            self.user_username = self.credentials.username
            self.local_server = self.credentials.local_server
        if self.user and not isinstance(self.user, DBRef):
            self.user_name = self.user.full_name
        if self.local_server and not isinstance(self.local_server, DBRef):
            self.local_server_name = self.local_server.name

    @classmethod
    def field_names_header_for_csv(cls):
        return ['Koombook id', 'Koombook name', 'User id', 'User username', 'User full name', 'Date - Time',
                'Action type', 'Object id', 'Object title', 'Object-specific data']

    def top_level_syncable_document(self):
        return self.user

    def all_synced_documents(self, local_server=None):
        if self.object and not isinstance(self.object, DBRef):
            if not local_server.syncs_document(self.object):
                return []
        return super(Activity, self).all_synced_documents(local_server=local_server)

    def __unicode__(self):
        return "Activity with type %s for user %s" % (self.type, self.user)

    def get_field_names_for_csv(self):
        """ this method gives the fields to export as csv row, in a chosen order """
        return ['local_server_id', 'local_server_name', 'user_id', 'user_username', 'user_name', 'date', 'type',
                'object', 'object_title']
