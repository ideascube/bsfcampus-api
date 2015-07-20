from flask import current_app

from MookAPI.core import Service
from .documents import LocalServer

class LocalServersService(Service):
    __model__ = LocalServer

    def get_by_key_secret(self, key, secret):
        from MookAPI.services import users
        user = users.get(username=key)
        user.verify_pass(secret)
        return self.get(user=user)

    def get_current(self):
        key = current_app.config.get('CENTRAL_SERVER_KEY', None)
        secret = current_app.config.get('CENTRAL_SERVER_SECRET', None)
        return self.get_by_key_secret(key, secret)
