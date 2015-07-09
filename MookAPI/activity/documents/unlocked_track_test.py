from MookAPI.core import db

from . import ActivityJsonSerializer, Activity


class UnlockedTrackTestJsonSerializer(ActivityJsonSerializer):
    pass


class UnlockedTrackTest(UnlockedTrackTestJsonSerializer, Activity):
    """
    Records when a resource is completed by a user
    """

    track = db.ReferenceField('Track')
