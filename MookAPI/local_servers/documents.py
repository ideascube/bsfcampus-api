from mongoengine import ValidationError
import datetime

from flask import url_for

from MookAPI.core import db
from MookAPI.helpers import JsonSerializer
from MookAPI.sync import SyncableDocument


class SyncableItemJsonSerializer(JsonSerializer):
    pass

class SyncableItem(SyncableItemJsonSerializer, db.EmbeddedDocument):
    """
    .. _SyncableItem:

    This embedded document contains a reference to an item (document) to synchronize, and the date it was last checked out by the local server.
    """

    ALLOWED_SERVICES = [
        'tracks',
        'users'
    ]

    ### PROPERTIES

    last_sync = db.DateTimeField()
    """The date of the last synchronization, *i.e.* the date when the list of updates to perform was last fetched."""

    document = db.GenericReferenceField()
    """A reference to the top-level ``SyncableDocument`` to synchronize."""

    ### METHODS

    def sync_list(self):
        """
        Returns a list of atomic documents whose ``top_level_document()`` is ``item`` and that have changed since ``last_sync``.
        """
        return self.document.items_to_sync(self.last_sync, local_server=self._instance)

    @classmethod
    def init_with_service_and_id(cls, service_name, document_id):
        services = __import__('MookAPI.services', globals(), locals(), [service_name], 0)
        service = getattr(services, service_name)
        document = service.get(document_id)

        return cls(document=document)

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


class LocalServerJsonSerializer(JsonSerializer):
    pass

class LocalServer(LocalServerJsonSerializer, SyncableDocument):
    """
    .. _LocalServer:

    This collection contains the list of all central servers connected to the current central server.
    """

    ### PROPERTIES

    user = db.ReferenceField('User', unique=True)
    """
    The ``User`` account associated to the ``LocalServer``.
    It must have a ``Role`` named ``local_server``.
    """

    ## List of items to synchronize
    syncable_items = db.ListField(db.EmbeddedDocumentField(SyncableItem))
    """A list of SyncableItem_ embedded documents describing the items to synchronize on the local server."""

    last_sync = db.DateTimeField()

    @property
    def url(self):
        return url_for("local_servers.get_local_server", local_server_id=self.id, _external=True)

    @property
    def synchronized_documents(self):
        return [item.document for item in self.syncable_items]

    def append_syncable_item(self, service_name, document_id):
        syncable_item = SyncableItem.init_with_service_and_id(service_name, document_id)
        if syncable_item.document not in self.synchronized_documents:
            self.syncable_items.append(syncable_item)

    def syncs_document(self, document):
        top_level_document = document.top_level_syncable_document()
        return top_level_document in self.synchronized_documents

    def all_syncable_items(self, local_server=None):
        items = self.user.all_syncable_items(local_server=local_server)
        items.extend(super(LocalServer, self).all_syncable_items(local_server=local_server))
        return items

    @staticmethod
    def _prepare_list(list):
        def _unique(l):
            seen = set()
            seen_add = seen.add
            return [x for x in l if not(x in seen or seen_add(x))]

        def _prioritize(l):
            def get_rank(item):
                    PRIORITIES = [
                        'Track',
                        'User',
                        'LocalServer',
                    ]
                    try:
                        return PRIORITIES.index(item.document.__class__.__name__)
                    except:
                        return float('inf')
            return sorted(l, key=get_rank)

        return _prioritize(_unique(list))

    def get_sync_list(self):
        updates = []
        deletes = []

        for (index, item) in enumerate(self.syncable_items):
            updates.extend(item.sync_list()['update'])
            deletes.extend(item.sync_list()['delete'])

        updates.extend(self.items_to_update(last_sync=self.last_sync, local_server=self))

        return self._prepare_list(updates), self._prepare_list(deletes)

    def set_last_sync(self, date):
        for item in self.syncable_items:
            item.last_sync = date
        self.last_sync = date

    def reset(self):
        self.set_last_sync(date=None)
