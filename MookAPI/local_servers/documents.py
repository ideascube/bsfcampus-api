from passlib.hash import bcrypt
from mongoengine import PULL

from flask import url_for

from MookAPI.core import db
from MookAPI.helpers import unique
from MookAPI.sync import SyncableDocumentJsonSerializer, SyncableDocument


class LocalServerJsonSerializer(SyncableDocumentJsonSerializer):
    __json_dbref__ = ['name', 'key']

class LocalServer(LocalServerJsonSerializer, SyncableDocument):
    """
    .. _LocalServer:

    This collection contains the list of all central servers connected to the current central server.
    """

    ### PROPERTIES

    name = db.StringField()

    key = db.StringField(unique=True)

    secret = db.StringField()

    synced_tracks = db.ListField(db.ReferenceField('Track', reverse_delete_rule=PULL))
    synced_users = db.ListField(db.ReferenceField('User', reverse_delete_rule=PULL))

    @property
    def synced_documents(self):
        documents = []
        documents.extend(self.synced_tracks)
        documents.extend(self.synced_users)
        return documents

    last_sync = db.DateTimeField()

    @property
    def url(self, _external=False):
        return url_for("local_servers.get_local_server", local_server_id=self.id, _external=_external)

    def syncs_document(self, document):
        top_level_document = document.top_level_syncable_document()
        return top_level_document in self.synced_documents

    def get_sync_list(self):
        updates = []
        deletes = []

        updates.extend(self.items_to_update(local_server=self))

        for document in self.synced_documents:
            updates.extend(document.items_to_update(local_server=self))
            deletes.extend(document.items_to_delete(local_server=self))

        return dict(
            updates=unique(updates),
            deletes=deletes # 'deletes' contains (unhashable) DBRef objects, can't apply 'unique' to it
        )

    def reset(self):
        self.last_sync = None

    def __unicode__(self):
        return "%s [%s]" % (self.name, self.key)

    @staticmethod
    def hash_secret(secret):
        """
        Return the md5 hash of the secret+salt
        """
        return bcrypt.encrypt(secret)

    def verify_secret(self, secret):
        return bcrypt.verify(secret, self.secret)
