from functools import wraps
from werkzeug.local import LocalProxy

from flask import jsonify, request, _request_ctx_stack

from flask_cors import CORS
from flask_jwt import JWT

import activity

cors = CORS()

jwt = JWT()

@jwt.authentication_handler
def authenticate(username, password):
    from MookAPI.services import misc_activities
    misc_activities.create(type="auth_attempt", object_title=username)
    try:
        from MookAPI.helpers import current_local_server, is_local
        from MookAPI.services import users, user_credentials
        local_server = current_local_server()
        if is_local() and not local_server:
            return None


        creds = user_credentials.get(
            username=username,
            local_server=local_server,
            password=password
        )
        if creds:
            if creds.user.active:
                misc_activities.create(
                    credentials=creds,
                    type="auth_success",
                    object_title=username
                )
                return creds
            else:
                misc_activities.create(
                    credentials=creds,
                    type="auth_fail",
                    object_title=username
                )
                return creds
        else:
            misc_activities.create(type="auth_fail", object_title=username)
            return None
    except:
        misc_activities.create(type="auth_fail", object_title=username)
        return None

@jwt.payload_handler
def make_payload(creds):
    return dict(
        creds_id=str(creds.id)
    )

@jwt.user_handler
def load_user(payload):
    creds_id = payload['creds_id']
    try:
        from MookAPI.services import user_credentials
        return user_credentials.get(id=creds_id)
    except:
        return None

def local_server_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth:
            return jsonify(error="Basic Authorization required"),\
                   401,\
                   {'WWW-Authenticate': 'Basic realm="Login required"'}
        from MookAPI.services import local_servers
        try:
            local_server = local_servers.get(key=auth.username, secret=auth.password)
        except:
            return jsonify(error="Invalid credentials"), \
                   401, \
                   {'WWW-Authenticate': 'Basic realm="Login required"'}
        _request_ctx_stack.top.authenticated_local_server = local_server
        return f(*args, **kwargs)
    return decorated

authenticated_local_server = LocalProxy(lambda: getattr(_request_ctx_stack.top, 'authenticated_local_server', None))
