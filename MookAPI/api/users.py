from mongoengine import NotUniqueError

from flask import Blueprint, request, jsonify, abort
from flask_jwt import current_user
from flask_mongoengine import ValidationError

from MookAPI.services import tracks, users, user_credentials
from MookAPI.auth import jwt_required

import activity

from . import route

bp = Blueprint('users', __name__, url_prefix="/users")

@route(bp, "/current", methods=['GET', 'PATCH'], jsonify_wrap=False)
@jwt_required()
def current_user_info():
    user = current_user.user

    if request.method == 'GET':
        return jsonify(data=user)

    elif request.method == 'PATCH':

        data = request.get_json()
        user.full_name = data['full_name']
        user.email = data['email']
        try:
            user.save()
        except ValidationError as e:
            response = {
                "error": "Could not update user",
                "message": e.message
            }
            return response, 400

        return jsonify(data=user)

@route(bp, "/current/password", methods=['PATCH'], jsonify_wrap=False)
@jwt_required()
def current_user_change_password():
    user = current_user.user

    if request.method == 'PATCH':

        data = request.get_json()
        if not user.verify_pass(data['current_password']):
            response = {
                "error": "Current password is wrong",
                "code": 1
            }
            return jsonify(response), 400

        new_password = data['new_password']
        if new_password is None or new_password == "":
            response = {
                "error": "The new password cannot be empty",
                "code": 2
            }
            return jsonify(response), 400

        confirm_password = data['confirm_new_password']
        if new_password != confirm_password:
            response = {
                "error": "Passwords don't match",
                "code": 3
            }
            return jsonify(response), 400

        user.password = users.__model__.hash_pass(new_password)
        try:
            user.save()
        except ValidationError as e:
            response = {
                "error": "Could not update user",
                "message": e.message
            }
            return response, 400

        return jsonify(data=user)


@route(bp, "/current/dashboard")
@jwt_required()
def current_user_dashboard():
    user = current_user.user

    dashboard = dict(
        user=user,
        tracks=[]
    )
    for track in tracks.all().order_by('order'):
        dashboard['tracks'].append(track.encode_mongo_for_dashboard(user))

    return dashboard


@route(bp, "/<user_id>")
# @jwt_required()
def get_user_info(user_id):
    return users.get_or_404(user_id)

@route(bp, "/<user_id>/dashboard")
@jwt_required()
def user_dashboard(user_id):
    requested_user = users.get_or_404(user_id)
    from MookAPI.services import visited_user_dashboards
    user = current_user.user
    visited_user_dashboards.create(user=user, dashboard_user=requested_user)

    dashboard = dict(
        user=requested_user,
        tracks=[]
    )
    for track in tracks.all():
        dashboard['tracks'].append(track.encode_mongo_for_dashboard(requested_user))
    dashboard['tracks'].sort(key=lambda t: t['order'])

    return dashboard


@route(bp, "/register", methods=['POST'], jsonify_wrap=False)
def register_user():
    """Registers a new user"""
    activity.record_simple_misc_analytic("register_user_attempt")

    data = request.get_json()
    password = data['password']
    if password is None or password == "":
        response = {
            "error": "The password cannot be empty",
            "code": 4
        }
        return jsonify(response), 400

    if password != data['password_confirm']:
        response = {
            "error": "Passwords don't match",
            "code": 5
        }
        return jsonify(response), 400

    if 'accept_cgu' not in data:
        response = {
            "error": "User must accept cgu",
            "code": 6
        }
        return jsonify(response), 400

    username = data['username']
    full_name = data['full_name']
    if not full_name:
        full_name = username

    new_user = users.new(
        full_name=full_name,
        email=data['email'],
        accept_cgu='accept_cgu' in data
    )

    try:
        new_user.save()

    except ValidationError as e:
        response = {
            "error": "Could not create user",
            "message": e.message,
            "code": 2
        }
        return jsonify(response), 400

    except NotUniqueError as e:
        response = {
            "error": "This username already belongs to someone",
            "message": e.message,
            "code": 3
        }
        return jsonify(response), 400

    except Exception as e:
        response = {
            "error": "Unrecognized exception",
            "message": e.message,
            "code": 1
        }
        return jsonify(response), 400

    else:
        from MookAPI.helpers import current_local_server
        local_server = current_local_server()
        user_credentials.create(
            user=new_user,
            username=username,
            password=password,
            local_server=local_server
        )
        ## Password is automatically hashed in the Service.

        local_server.append_syncable_item(document=new_user)
        local_server.save()

        activity.record_misc_analytic("register_user_attempt", "success")
        return jsonify(data=new_user)

@route(bp, "/search/<username>", methods=['GET'])
def search_users(username):
    from MookAPI.helpers import current_local_server
    local_server = current_local_server()
    credentials = user_credentials.find(username=username, local_server=local_server)

    return [creds.user for creds in credentials]

@route(bp, "/phagocyte", methods=['POST'])
@jwt_required()
def absorb_user():
    data = request.get_json()
    local_server = data.get('local_server', None)
    username = data.get('username', None)
    password = data.get('password', None)

    creds = user_credentials.get(
        local_server=local_server,
        username=username,
        password=password
    )

    if not creds:
        abort(404)

    user = current_user.user

    user.phagocyte(other=creds.user)

    return user
