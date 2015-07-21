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
        'allow_inheritance': True
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

    def clean(self):
        super(Activity, self).clean()
        if self.object:
            self.object_title = getattr(self.object, 'title', None)
        if self.credentials:
            self.user = self.credentials.user
            self.user_username = self.credentials.username
            self.local_server = self.credentials.local_server
        if self.user:
            self.user_name = self.user.full_name
        if self.local_server:
            self.local_server_name = self.local_server.name

    @classmethod
    def field_names_header_for_csv(cls):
        return ['Koombook id', 'Koombook name', 'User id', 'User username', 'User full name', 'Date - Time',
                'Action type', 'Object id', 'Object title', 'Object-specific data']

    @property
    def url(self):
        print("Activity (%s) url: %s" % (self._cls, self.id))
        return url_for("activity.get_activity", activity_id=self.id, _external=True)

    def top_level_syncable_document(self):
        return self.user

    def all_syncable_items(self, local_server=None):
        if self.object:
            if not local_server.syncs_document(self.object):
                return []
        return super(Activity, self).all_syncable_items(local_server=local_server)

    def __unicode__(self):
        return "Activity with type %s for user %s" % (self.type, self.user)

    def get_field_names_for_csv(self):
        """ this method gives the fields to export as csv row, in a chosen order """
        return ['local_server_username', 'local_server_name', 'user', 'user_username', 'user_name', 'date', 'type',
                'object', 'object_title']
