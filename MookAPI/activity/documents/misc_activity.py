from MookAPI.core import db

from . import ActivityJsonSerializer, Activity


class MiscActivityJsonSerializer(ActivityJsonSerializer):
    pass


class MiscActivity(MiscActivityJsonSerializer, Activity):
    """
    Records any other activity (which doesn't have a specific object linked to it)
    """

    def __init__(self, *args, **kwargs):
        super(MiscActivity, self).__init__(*args, **kwargs)

        self.type = kwargs.pop('misc_type', '')
        self.activity_title = kwargs.pop('misc_title', '')
