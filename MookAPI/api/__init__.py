from functools import wraps
from flask import jsonify

from MookAPI.serialization import JSONEncoder
from MookAPI import factory

def create_app(settings_override=None, register_security_blueprint=False):

    app = factory.create_app(
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
    jsonify_wrap = kwargs.pop('jsonify_wrap', True)

    def decorator(f):
        @bp.route(*args, **kwargs)
        @wraps(f)
        def wrapper(*args, **kwargs):
            sc = 200
            rv = f(*args, **kwargs)
            if isinstance(rv, tuple):
                sc = rv[1]
                rv = rv[0]
            if jsonify_wrap:
                return jsonify(dict(data=rv)), sc
            else:
                return rv, sc
        return f

    return decorator
