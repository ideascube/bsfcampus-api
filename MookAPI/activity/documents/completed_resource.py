from MookAPI.core import db

from . import ActivityJsonSerializer, Activity


class CompletedResourceJsonSerializer(ActivityJsonSerializer):
    pass


class CompletedResource(CompletedResourceJsonSerializer, Activity):
    """
    Records when a resource is completed by a user
    """

    resource = db.ReferenceField('Resource')

    def all_syncable_items(self, local_server=None):
        top_level_syncable_document = self.resource.top_level_syncable_document()
        if local_server:
            if local_server.syncs_document(top_level_syncable_document):
                return super(CompletedResource, self).all_syncable_items(local_server=local_server)
        return []
