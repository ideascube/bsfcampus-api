from MookAPI.core import db

from . import ActivityJsonSerializer, Activity


class CompletedResourceJsonSerializer(ActivityJsonSerializer):
    pass


class CompletedResource(CompletedResourceJsonSerializer, Activity):
    """
    Records when a resource is completed by a user
    """

    resource = db.ReferenceField('Resource')
