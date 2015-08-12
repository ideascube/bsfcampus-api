from functools import wraps
from flask import jsonify
from mongoengine import QuerySet

from MookAPI.core import db
from MookAPI.factory import create_app as create_base_app
from MookAPI.serialization import JSONEncoder

def create_app(settings_override=None, register_security_blueprint=False):

    app = create_base_app(
        __name__,
        __path__,
        settings_override,
        register_security_blueprint=register_security_blueprint
    )

    app.json_encoder = JSONEncoder

    from ._mail import mail
    from ._security import cors, jwt

    mail.init_app(app)
    cors.init_app(app)
    jwt.init_app(app)

    return app

def route(bp, *args, **kwargs):

    kwargs.setdefault('strict_slashes', False)

    def decorator(f):
        @bp.route(*args, **kwargs)
        @wraps(f)
        def wrapper(*args, **kwargs):
            sc = 200
            rv = f(*args, **kwargs)
            if isinstance(rv, tuple):
                sc = rv[1]
                rv = rv[0]
            if isinstance(rv, (db.Document, QuerySet)):
                rv = jsonify(data=rv)
            return rv, sc
        return f

    return decorator
