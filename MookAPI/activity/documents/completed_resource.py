from MookAPI.core import db

from . import ActivityJsonSerializer, Activity


class CompletedResourceJsonSerializer(ActivityJsonSerializer):
    pass


class CompletedResource(CompletedResourceJsonSerializer, Activity):
    """
    Records when a resource is completed by a user
    """

    resource = db.ReferenceField('Resource')

    def clean(self):
        super(CompletedResource, self).clean()
        self.type = "completed_resource"
        if self.resource:
            self.activity_id = self.resource.id
            self.activity_title = self.resource.title
