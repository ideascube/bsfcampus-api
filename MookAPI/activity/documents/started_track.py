from MookAPI.core import db

from . import ActivityJsonSerializer, Activity


class StartedTrackJsonSerializer(ActivityJsonSerializer):
    pass


class StartedTrack(StartedTrackJsonSerializer, Activity):
    """
    Records when a resource is completed by a user
    """

    track = db.ReferenceField('Track')

    def __init__(self, **kwargs):
        super(StartedTrack, self).__init__(**kwargs)
        self.type = "started_track"
        self.resource = kwargs.pop('track', None)
