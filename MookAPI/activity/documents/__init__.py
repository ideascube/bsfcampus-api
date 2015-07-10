import datetime

from flask import url_for

from MookAPI.core import db
from MookAPI.helpers import JsonSerializer
from MookAPI.sync import SyncableDocument


class ActivityJsonSerializer(JsonSerializer):
    pass

class Activity(ActivityJsonSerializer, SyncableDocument):
    """Describes any kind of user activity."""

    meta = {
        'allow_inheritance': True
    }

    ### PROPERTIES

    user = db.ReferenceField('User')
    """The user performing the activity."""

    date = db.DateTimeField(default=datetime.datetime.now, required=True)
    """The date at which the activity was performed."""

    @property
    def url(self):
        return url_for("activity.get_activity", activity_id=self.id, _external=True)

    def top_level_syncable_document(self):
        return self.user
