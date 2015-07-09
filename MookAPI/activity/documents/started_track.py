from MookAPI.core import db

from . import ActivityJsonSerializer, Activity


class StartedTrackJsonSerializer(ActivityJsonSerializer):
    pass


class StartedTrack(StartedTrackJsonSerializer, Activity):
    """
    Records when a resource is completed by a user
    """

    track = db.ReferenceField('Track')