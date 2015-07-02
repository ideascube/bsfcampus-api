from flask_jwt import JWTError, _jwt, _request_ctx_stack
from flask import current_app, request
from itsdangerous import (
    SignatureExpired,
    BadSignature
)
from functools import wraps

def jwt_required(realm=None):
    """-Replaces the jwt_required decorator function from flask-JWT, so we can call the customized verify_jwt function-
    View decorator that requires a valid JWT token to be present in the request

    :param realm: an optional realm
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt(realm)
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def verify_jwt(realm=None):
    """-Replaces the verify_jwt function from flask-JWT, so we can set the error code to 401 for Invalid JWT request-
    Does the actual work of verifying the JWT data in the current request.
    This is done automatically for you by `jwt_required()` but you could call it manually.
    Doing so would be useful in the context of optional JWT access in your APIs.

    :param realm: an optional realm
    """
    realm = realm or current_app.config['JWT_DEFAULT_REALM']
    auth = request.headers.get('Authorization', None)

    if auth is None:
        raise JWTError('Authorization Required', 'Authorization header was missing', 401, {
            'WWW-Authenticate': 'JWT realm="%s"' % realm
        })

    parts = auth.split()

    if parts[0].lower() != 'bearer':
        raise JWTError('Invalid JWT header', 'Unsupported authorization type')
    elif len(parts) == 1:
        raise JWTError('Invalid JWT header', 'Token missing')
    elif len(parts) > 2:
        raise JWTError('Invalid JWT header', 'Token contains spaces')

    try:
        handler = _jwt.decode_callback
        payload = handler(parts[1])
    except SignatureExpired:
        raise JWTError('Invalid JWT', 'Token is expired', 401)
    except BadSignature:
        raise JWTError('Invalid JWT', 'Token is undecipherable', 401)

    _request_ctx_stack.top.current_user = user = _jwt.user_callback(payload)

    if user is None:
        raise JWTError('Invalid JWT', 'User does not exist', 401)
