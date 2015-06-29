from MookAPI.core import Service
from .documents import Role, User

class RolesService(Service):
    __model__ = Role

class UsersService(Service):
    __model__ = User
