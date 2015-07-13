from MookAPI.core import db

from . import ActivityJsonSerializer, Activity


class StartedTrackJsonSerializer(ActivityJsonSerializer):
    pass


class StartedTrack(StartedTrackJsonSerializer, Activity):
    """
    Records when a resource is completed by a user
    """

    track = db.ReferenceField('Track')

    def all_syncable_items(self, local_server=None):
        top_level_syncable_document = self.track.top_level_syncable_document()
        if local_server:
            if local_server.syncs_document(top_level_syncable_document):
                return super(StartedTrack, self).all_syncable_items(local_server=local_server)
        return []
