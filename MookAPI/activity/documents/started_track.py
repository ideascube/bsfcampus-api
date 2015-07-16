from MookAPI.core import db

from . import ActivityJsonSerializer, Activity


class StartedTrackJsonSerializer(ActivityJsonSerializer):
    pass


class StartedTrack(StartedTrackJsonSerializer, Activity):
    """
    Records when a resource is completed by a user
    """

    track = db.ReferenceField('Track')

    def __init__(self, *args, **kwargs):
        super(StartedTrack, self).__init__(*args, **kwargs)
        self.type = "started_track"
        self.track = kwargs.pop('track', None)
