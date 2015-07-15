from MookAPI.core import db

from . import ActivityJsonSerializer, Activity


class CompletedTrackJsonSerializer(ActivityJsonSerializer):
    pass


class CompletedTrack(CompletedTrackJsonSerializer, Activity):
    """
    Records when a resource is completed by a user
    """

    track = db.ReferenceField('Track')

    def __init__(self, **kwargs):
        super(CompletedTrack, self).__init__(**kwargs)
        self.type = "completed_track"
        self.resource = kwargs.pop('track', None)
