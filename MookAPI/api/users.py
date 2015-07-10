from mongoengine import NotUniqueError

from flask import Blueprint, request, jsonify
from flask_jwt import current_user
from flask_mongoengine import ValidationError

from MookAPI.services import tracks, users
from MookAPI.auth import jwt_required

from . import route

bp = Blueprint('users', __name__, url_prefix="/users")

@route(bp, "/current", methods=['GET', 'PATCH'])
@jwt_required()
def current_user_info():
    user = current_user._get_current_object()

    if request.method == 'GET':
        return jsonify(dict(data=user))

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

        return jsonify(dict(data=user))

@route(bp, "/current/password", methods=['PATCH'])
@jwt_required()
def current_user_change_password():
    user = current_user._get_current_object()

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

        return jsonify(dict(data=user))


@route(bp, "/current/dashboard")
@jwt_required()
def current_user_dashboard():
    user = current_user._get_current_object()

    dashboard = dict(
        user=user,
        tracks=[]
    )
    for track in tracks.all():
        dashboard['tracks'].append(track.encode_mongo_for_dashboard(user))
    dashboard['tracks'].sort(key=lambda t: t['order'])

    return jsonify(data=dashboard)


@route(bp, "/<user_id>")
# @jwt_required()
def get_user_info(user_id):
    user = users.get_or_404(user_id)
    return jsonify(dict(data=user))

@route(bp, "/<user_id>/dashboard")
@jwt_required()
def user_dashboard(user_id):
    user = users.get_or_404(user_id)

    dashboard = dict(
        user=user,
        tracks=[]
    )
    for track in tracks.all():
        dashboard['tracks'].append(track.encode_mongo_for_dashboard(user))
    dashboard['tracks'].sort(key=lambda t: t['order'])

    return jsonify(data=dashboard)


@route(bp, "/register", methods=['POST'])
def register_user():
        """Registers a new user"""

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
        if full_name == "" or full_name is None:
            full_name = username

        new_user = users.new(
            full_name=full_name,
            username=username,
            email=data['email'],
            password=users.__model__.hash_pass(password),
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
            return jsonify(data=new_user)
