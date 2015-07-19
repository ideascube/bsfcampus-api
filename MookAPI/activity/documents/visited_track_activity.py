from MookAPI.core import db

from . import ActivityJsonSerializer, Activity


class VisitedTrackJsonSerializer(ActivityJsonSerializer):
    pass


class VisitedTrack(VisitedTrackJsonSerializer, Activity):
    """
    Records when a track is visited by a user
    """

    track = db.ReferenceField('Track')

    @property
    def object(self):
        return self.track

    def clean(self):
        super(VisitedTrack, self).clean()
        self.type = "visited_track"
