from MookAPI.core import Service
from .documents import ItemToSync

class ItemsToSyncService(Service):
    __model__ = ItemToSync
