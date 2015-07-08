from MookAPI.core import db
from MookAPI.helpers import JsonSerializer
from MookAPI.hierarchy import TracksService
from MookAPI.users import UsersService

class SyncableItemJsonSerializer(JsonSerializer):
    pass

class SyncableItem(SyncableItemJsonSerializer, db.EmbeddedDocument):
    """
    .. _SyncableItem:

    This embedded document contains a reference to an item (document) to synchronize, and the date it was last checked out by the local server.
    """

    ### PROPERTIES

    last_sync = db.DateTimeField()
    """The date of the last synchronization, *i.e.* the date when the list of updates to perform was last fetched."""

    ## The item to synchronize
    ## Any item referenced in this field must be a subclass of SyncableDocument
    item = db.ReferenceField(TracksService.__model__)
    """A reference to the top-level ``SyncableDocument`` to synchronize."""

    ### METHODS

    def sync_list(self):
        """
        Returns a list of atomic documents whose ``top_level_document()`` is ``item`` and that have changed since ``last_sync``.
        """
        return self.item.items_to_sync(self.last_sync)


class LocalServerJsonSerializer(JsonSerializer):
    pass

class LocalServer(LocalServerJsonSerializer, db.Document):
    """
    .. _LocalServer:

    This collection contains the list of all central servers connected to the current central server.
    """

    ### PROPERTIES

    user = db.ReferenceField(UsersService.__model__, unique=True)
    """
    The ``User`` account associated to the ``LocalServer``.
    It must have a ``Role`` named ``local_server``.
    """

    ## List of items to synchronize
    syncable_items = db.ListField(db.EmbeddedDocumentField(SyncableItem))
    """A list of SyncableItem_ embedded documents describing the items to synchronize on the local server."""
