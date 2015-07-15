from MookAPI.core import db

from . import ActivityJsonSerializer, Activity


class UnlockedTrackTestJsonSerializer(ActivityJsonSerializer):
    pass


class UnlockedTrackTest(UnlockedTrackTestJsonSerializer, Activity):
    """
    Records when a resource is completed by a user
    """

    track = db.ReferenceField('Track')

    def __init__(self, **kwargs):
        super(UnlockedTrackTest, self).__init__(**kwargs)
        self.type = "unlocked_track_test"
        self.resource = kwargs.pop('track', None)
