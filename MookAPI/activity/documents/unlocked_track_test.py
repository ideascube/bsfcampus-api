from MookAPI.core import db

from . import ActivityJsonSerializer, Activity


class UnlockedTrackTestJsonSerializer(ActivityJsonSerializer):
    pass


class UnlockedTrackTest(UnlockedTrackTestJsonSerializer, Activity):
    """
    Records when a resource is completed by a user
    """

    track = db.ReferenceField('Track')

    def clean(self):
        super(UnlockedTrackTest, self).clean()
        self.type = "unlocked_track_test"
