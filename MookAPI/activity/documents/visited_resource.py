from MookAPI.core import db

from . import ActivityJsonSerializer, Activity


class VisitedResourceJsonSerializer(ActivityJsonSerializer):
    pass


class VisitedResource(VisitedResourceJsonSerializer, Activity):
    """
    Records when a resource is visited by a user
    """

    resource = db.ReferenceField('Resource')

    @property
    def object(self):
        return self.resource

    def clean(self):
        super(VisitedResource, self).clean()
        self.type = "visited_resource"
