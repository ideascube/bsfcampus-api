from functools import wraps
from werkzeug.local import LocalProxy

from flask import jsonify, request, Response, _request_ctx_stack

from flask_cors import CORS
from flask_jwt import JWT

import activity

cors = CORS()

jwt = JWT()

@jwt.authentication_handler
def authenticate(username, password):
    activity.record_misc_analytic("auth_attempt", username)
    try:
        from MookAPI.services import users
        user = users.first(username=username)
        if user.verify_pass(password):
            activity.record_misc_analytic("auth_success", username)
            return user
        else:
            activity.record_misc_analytic("auth_fail", username)
            return None
    except:
        activity.record_misc_analytic("auth_fail", username)
        return None

@jwt.payload_handler
def make_payload(user):
    return dict(user_id=str(user.id))

@jwt.user_handler
def load_user(payload):
    user_id = payload['user_id']
    try:
        from MookAPI.services import users
        user = users.get(user_id)
    except:
        return None
    else:
        return user

def basic_auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth:
            return jsonify(error="Basic Authorization required"),\
                   401,\
                   {'WWW-Authenticate': 'Basic realm="Login required"'}
        user = authenticate(auth.username, auth.password)
        if not user:
            return jsonify(error="Invalid credentials"), \
                   401, \
                   {'WWW-Authenticate': 'Basic realm="Login required"'}
        _request_ctx_stack.top.basic_auth_user = user
        return f(*args, **kwargs)
    return decorated

basic_auth_user = LocalProxy(lambda: getattr(_request_ctx_stack.top, 'basic_auth_user', None))
