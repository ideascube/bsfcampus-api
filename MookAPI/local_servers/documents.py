import requests

import flask

from MookAPI import db
import MookAPI.mongo_coder as mc

from MookAPI.users.documents import User
from MookAPI.hierarchy.documents import track


class SyncableItem(mc.MongoCoderEmbeddedDocument):
    """
    .. _SyncableItem:

    This embedded document contains a reference to an item (document) to synchronize, and the date it was last checked out by the local server.
    """

    ### PROPERTIES

    last_sync = db.DateTimeField()
    """The date of the last synchronization, *i.e.* the date when the list of updates to perform was last fetched."""

    ## The item to synchronize
    ## Any item referenced in this field must be a subclass of SyncableDocument
    item = db.ReferenceField(track.Track)
    """A reference to the top-level ``SyncableDocument`` to synchronize."""

    ### METHODS

    def sync_list(self):
        """
        Returns a list of atomic documents whose ``top_level_document()`` is ``item`` and that have changed since ``last_sync``.
        """
        return self.item.items_to_sync(self.last_sync)


class LocalServer(mc.MongoCoderDocument):
    """
    .. _LocalServer:

    This collection contains the list of all central servers connected to the current central server.
    """

    ### PROPERTIES

    user = db.ReferenceField(User, unique=True)
    """
    The ``User`` account associated to the ``LocalServer``.
    It must have a ``Role`` named ``local_server``.
    """

    ## List of items to synchronize
    syncable_items = db.ListField(db.EmbeddedDocumentField(SyncableItem))
    """A list of SyncableItem_ embedded documents describing the items to synchronize on the local server."""

    @classmethod
    def json_key(cls):
        return 'local_server'  # At some point we should have the parent class do the underscoring automatically.
