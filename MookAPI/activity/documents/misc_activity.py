from MookAPI.core import db

from . import ActivityJsonSerializer, Activity


class MiscActivityJsonSerializer(ActivityJsonSerializer):
    pass


class MiscActivity(MiscActivityJsonSerializer, Activity):
    """
    Records any other activity (which doesn't have a specific object linked to it)
    """
    pass
