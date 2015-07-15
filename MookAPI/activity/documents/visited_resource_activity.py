from MookAPI.core import db

from . import ActivityJsonSerializer, Activity


class VisitedResourceJsonSerializer(ActivityJsonSerializer):
    pass


class VisitedResource(VisitedResourceJsonSerializer, Activity):
    """
    Records when a resource is visited by a user
    """

    resource = db.ReferenceField('Resource')

    def __init__(self, **kwargs):
        super(VisitedResource, self).__init__(**kwargs)
        self.type = "visited_resource"
        self.resource = kwargs.pop('resource', None)

    def clean(self):
        super(VisitedResource, self).clean()
        if self.resource:
            self.activity_id = self.resource.id
            self.activity_title = self.resource.title
