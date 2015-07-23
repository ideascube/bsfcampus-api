from passlib.hash import bcrypt
from mongoengine import ValidationError

from flask import url_for

from MookAPI.core import db
from MookAPI.serialization import JsonSerializer
from MookAPI.sync import SyncableDocumentJsonSerializer, SyncableDocument


class SyncableItemJsonSerializer(SyncableDocumentJsonSerializer):
    pass

class SyncableItem(SyncableItemJsonSerializer, db.EmbeddedDocument):
    """
    .. _SyncableItem:

    This embedded document contains a reference to an item (document) to synchronize, and the date it was last checked out by the local server.
    """

    meta = {
        'allow_inheritance': True
    }

    ALLOWED_SERVICES = [
        'tracks',
        'users'
    ]

    ### PROPERTIES

    last_sync = db.DateTimeField()
    """The date of the last synchronization, *i.e.* the date when the list of updates to perform was last fetched."""

    # document = db.ReferenceField('SyncableDocument')
    # """A reference to the top-level ``SyncableDocument`` to synchronize."""

    ### METHODS

    def sync_list(self):
        """
        Returns a list of atomic documents whose ``top_level_document()`` is ``item`` and that have changed since ``last_sync``.
        """
        return self.document.items_to_sync(self.last_sync, local_server=self._instance)

    def validate(self, clean=True):
        super(SyncableItem, self).validate(clean)

        import MookAPI.services
        document_type_allowed = False
        for service_name in self.ALLOWED_SERVICES:
            service = getattr(MookAPI.services, service_name, None)
            if service and service._isinstance(self.document):
                document_type_allowed = True
                break

        if not document_type_allowed:
            document_error = "Document type %s not allowed" % self.document.__class__.__name__
            errors = dict(document=document_error)
            pk = "None"
            if self._instance and hasattr(self._instance, 'pk'):
                pk = self._instance.pk
            message = "ValidationError (%s:%s) " % (self._class_name, pk)
            raise ValidationError(message, errors=errors)


class SyncableTrack(SyncableItem):
    document = db.ReferenceField('Track')

class SyncableUser(SyncableItem):
    document = db.ReferenceField('User')

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

    syncable_tracks = db.ListField(db.EmbeddedDocumentField(SyncableTrack))
    syncable_users = db.ListField(db.EmbeddedDocumentField(SyncableUser))

    @property
    def syncable_items(self):
        items = []
        items.extend(self.syncable_tracks)
        items.extend(self.syncable_users)
        return items

    last_sync = db.DateTimeField()

    @property
    def url(self):
        return url_for("local_servers.get_local_server", local_server_id=self.id, _external=True)

    @property
    def synchronized_documents(self):
        return [item.document for item in self.syncable_items]

    def append_syncable_item(self, document=None, **kwargs):
        from MookAPI.services import tracks, users
        if not document:
            service_name = kwargs.pop('service_name', None)
            document_id = kwargs.pop('document_id', None)

            if not (service_name and document_id):
                raise Exception("You need to provide a document, or a service_name and a document_id")

            if service_name == 'users':
                document = users.get(document_id)
            elif service_name == 'tracks':
                document = tracks.get(document_id)

        if document and document not in self.synchronized_documents:
            if users._isinstance(document):
                syncable_user = SyncableUser(document=document)
                self.syncable_users.append(syncable_user)
            elif tracks._isinstance(document):
                syncable_track = SyncableTrack(document=document)
                self.syncable_tracks.append(syncable_track)

    def syncs_document(self, document):
        top_level_document = document.top_level_syncable_document()
        return top_level_document in self.synchronized_documents

    @staticmethod
    def _unique(list):
        seen = set()
        seen_add = seen.add
        return [x for x in list if not(x in seen or seen_add(x))]

    def get_sync_list(self):
        updates = []
        deletes = []

        for (index, item) in enumerate(self.syncable_items):
            updates.extend(item.sync_list()['update'])
            deletes.extend(item.sync_list()['delete'])

        updates.extend(self.items_to_update(last_sync=self.last_sync, local_server=self))

        return self._unique(updates), self._unique(deletes)

    def set_last_sync(self, date):
        for item in self.syncable_items:
            item.last_sync = date
        self.last_sync = date

    def reset(self):
        self.set_last_sync(date=None)

    def __unicode__(self):
        return self.name

    @staticmethod
    def hash_secret(secret):
        """
        Return the md5 hash of the secret+salt
        """
        return bcrypt.encrypt(secret)

    def verify_secret(self, secret):
        return bcrypt.verify(secret, self.secret)
