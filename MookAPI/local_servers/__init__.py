from flask import current_app

from MookAPI.core import Service
from .documents import LocalServer

class LocalServersService(Service):
    __model__ = LocalServer

    def _preprocess_params(self, kwargs):
        secret = kwargs.get('secret', None)
        if secret:
            hashed_secret = self.__model__.hash_secret(secret)
            kwargs['secret'] = hashed_secret
        return super(LocalServersService, self)._preprocess_params(kwargs)

    def get(self, id=None, **kwargs):
        secret = kwargs.pop('secret', None)
        local_server = super(LocalServersService, self).get(id=id, **kwargs)
        if secret:
            if local_server.verify_secret(secret):
                return local_server
            else:
                return None
        else:
            return local_server

    def get_current(self):
        key = current_app.config.get('CENTRAL_SERVER_KEY', None)
        secret = current_app.config.get('CENTRAL_SERVER_SECRET', None)
        return self.get(key=key, secret=secret)
