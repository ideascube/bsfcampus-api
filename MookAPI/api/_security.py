from flask_cors import CORS
from flask_jwt import JWT

cors = CORS()

jwt = JWT()

@jwt.authentication_handler
def authenticate(username, password):
    try:
        from MookAPI.services import users
        user = users.first(username=username)
        if user.verify_pass(password):
            return user
        else:
            return None
    except:
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
