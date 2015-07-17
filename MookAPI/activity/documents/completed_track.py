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
        if self.track:
            self.activity_id = self.track.id
            self.activity_title = self.track.title
