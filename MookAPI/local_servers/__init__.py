from MookAPI.core import Service
from .documents import LocalServer

class LocalServersService(Service):
    __model__ = LocalServer
