from MookAPI.core import db

from . import ActivityJsonSerializer, Activity


class CompletedResourceJsonSerializer(ActivityJsonSerializer):
    pass


class CompletedResource(CompletedResourceJsonSerializer, Activity):
    """
    Records when a resource is completed by a user
    """

    resource = db.ReferenceField('Resource')

    @property
    def object(self):
        return self.resource

    def clean(self):
        super(CompletedResource, self).clean()
        self.type = "completed_resource"
