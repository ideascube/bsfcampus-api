import datetime

from flask import url_for

from MookAPI.core import db
from MookAPI.helpers import JsonSerializer, CsvSerializer
from MookAPI.sync import SyncableDocumentJsonSerializer, SyncableDocument
from flask_jwt import current_user


class ActivityJsonSerializer(SyncableDocumentJsonSerializer):
    pass


class Activity(ActivityJsonSerializer, CsvSerializer, SyncableDocument):
    """Describes any kind of user activity."""

    meta = {
        'allow_inheritance': True
    }

    ### PROPERTIES

    user = db.ReferenceField('User')
    """The user performing the activity."""

    user_username = db.StringField(default="")
    """The username (= unique id) of the user who has performed the activity"""

    user_name = db.StringField(default="")
    """The full name of the user who has performed the activity"""

    date = db.DateTimeField(default=datetime.datetime.now, required=True)
    """The date at which the activity was performed."""

    local_server_username = db.StringField()
    """The username (= unique id) of the local server on which the activity has been performed"""

    local_server_name = db.StringField()
    """The full name of the local server on which the activity has been performed"""

    type = db.StringField()
    """ The type of the activity, so we can group the activities by type to better analyse them.
    This is supposed to be defaulted/initialized in each subclass"""

    activity_id = db.ObjectIdField()
    """ The object id of the object associated to this activity (Resource, Track, Skill, Exercise, or something else).
    This is supposed to be defaulted/initialized in each subclass """

    activity_title = db.StringField()
    """ The title of the object associated to this activity. It allows a better comprehension of the activity than the activity_id.
    This is supposed to be defaulted/initialized in each subclass """

    def clean(self):
        super(Activity, self).clean()
        if self.user:
            self.user_username = self.user.username
            self.user_name = self.user.full_name

    @classmethod
    def field_names_header_for_csv(cls):
        return ['Koombook id', 'Koombook name', 'User id', 'User username', 'User full name', 'Date - Time',
                'Action type', 'Action id', 'Action title', 'Action specific data']

    @property
    def url(self):
        print("Activity (%s) url: %s" % (self._cls, self.id))
        return url_for("activity.get_activity", activity_id=self.id, _external=True)

    def top_level_syncable_document(self):
        return self.user

    def __unicode__(self):
        return "Activity with type %s for user %s" % (self.type, self.user)

    def get_field_names_for_csv(self):
        """ this method gives the fields to export as csv row, in a chosen order """
        return ['local_server_username', 'local_server_name', 'user', 'user_username', 'user_name', 'date', 'type',
                'activity_id', 'activity_title']
