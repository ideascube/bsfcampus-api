from MookAPI.core import db

from . import ActivityJsonSerializer, Activity


class CompletedTrackJsonSerializer(ActivityJsonSerializer):
    pass


class CompletedTrack(CompletedTrackJsonSerializer, Activity):
    """
    Records when a resource is completed by a user
    """

    track = db.ReferenceField('Track')

    def __init__(self, *args, **kwargs):
        super(CompletedTrack, self).__init__(*args, **kwargs)
        self.type = "completed_track"
        self.track = kwargs.pop('track', None)
