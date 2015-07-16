from MookAPI.core import db

from . import ActivityJsonSerializer, Activity


class CompletedTrackJsonSerializer(ActivityJsonSerializer):
    pass


class CompletedTrack(CompletedTrackJsonSerializer, Activity):
    """
    Records when a resource is completed by a user
    """

    track = db.ReferenceField('Track')

    def clean(self):
        super(CompletedTrack, self).clean()
        self.type = "completed_track"
