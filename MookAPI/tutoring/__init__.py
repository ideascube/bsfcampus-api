from MookAPI.core import Service
from .documents import TutoringRelation

class TutoringRelationsService(Service):
    __model__ = TutoringRelation
