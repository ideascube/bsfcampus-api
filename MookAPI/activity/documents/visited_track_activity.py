from MookAPI.core import db

from . import ActivityJsonSerializer, Activity


class VisitedTrackJsonSerializer(ActivityJsonSerializer):
    pass


class VisitedTrack(VisitedTrackJsonSerializer, Activity):
    """
    Records when a track is visited by a user
    """

    track = db.ReferenceField('Track')

    def __init__(self, **kwargs):
        super(VisitedTrack, self).__init__(**kwargs)
        self.type = "visited_track"
        self.track = kwargs.pop('track')

    def clean(self):
        super(VisitedTrack, self).clean()
        if self.track:
            self.activity_id = self.track.id
            self.activity_title = self.track.title
