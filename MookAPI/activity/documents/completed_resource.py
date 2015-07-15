from MookAPI.core import db

from . import ActivityJsonSerializer, Activity


class CompletedResourceJsonSerializer(ActivityJsonSerializer):
    pass


class CompletedResource(CompletedResourceJsonSerializer, Activity):
    """
    Records when a resource is completed by a user
    """

    resource = db.ReferenceField('Resource')

    def __init__(self, **kwargs):
        super(CompletedResource, self).__init__(**kwargs)
        self.type = "completed_resource"
        self.resource = kwargs.pop('resource', None)
