import pkgutil
import importlib

from flask import Blueprint, current_app

def is_local():
    server_type = current_app.config.get('SERVER_TYPE', 'central')
    return server_type == 'local'

def is_central():
    return not is_local()

def _get_service_for_class(class_name):
    from .core import Service
    import MookAPI.services as s
    class_name = class_name.split('.')[-1]
    for name, service in s.__dict__.iteritems():
        if isinstance(service, Service):
            if service.__model__.__name__ == class_name:
                return service
    return None

def register_blueprints(app, package_name, package_path):
    rv = []
    for _, name, _ in pkgutil.iter_modules(package_path):
        m = importlib.import_module('%s.%s' % (package_name, name))
        for item in dir(m):
            item = getattr(m, item)
            if isinstance(item, Blueprint):
                app.register_blueprint(item)
            rv.append(item)
    return rv
