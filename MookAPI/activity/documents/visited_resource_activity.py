from MookAPI.core import db

from . import ActivityJsonSerializer, Activity


class VisitedResourceJsonSerializer(ActivityJsonSerializer):
    pass


class VisitedResource(VisitedResourceJsonSerializer, Activity):
    """
    Records when a resource is visited by a user
    """

    resource = db.ReferenceField('Resource')

    def clean(self):
        super(VisitedResource, self).clean()
        self.type = "visited_resource"
        if self.resource:
            self.activity_id = self.resource.id
            self.activity_title = self.resource.title
