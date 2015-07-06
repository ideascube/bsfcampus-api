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
@jwt_required()
def user_info(user_id):
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
        if data['password'] != data['password_confirm']:
            response = {
                "error": "Passwords don't match"
            }
            return jsonify(response), 400

        new_user = users.new(
            full_name=data['full_name'],
            username=data['username'],
            email=data['email'],
            password=users.__model__.hash_pass(data['password']),
            accept_cgu=data['accept_cgu'] in ['1', 1, 'on']
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
