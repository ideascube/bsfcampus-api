import datetime

from MookAPI.core import db
from MookAPI.helpers import JsonSerializer
from MookAPI.sync import SyncableDocument


class ActivityJsonSerializer(JsonSerializer):
    pass

class Activity(ActivityJsonSerializer, SyncableDocument):
    """Describes any kind of user activity."""

    meta = {
        'allow_inheritance': True,
        'abstract': True
    }

    ### PROPERTIES

    # user = db.ReferenceField('User', required=True)
    # """The user performing the activity."""

    date = db.DateTimeField(default=datetime.datetime.now, required=True)
    """The date at which the activity was performed."""
