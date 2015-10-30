# -*- coding: utf-8 -*-

from bson import ObjectId
from mongoengine import NotUniqueError, DoesNotExist
import random
import string

from flask import Blueprint, request, jsonify, current_app
from flask_jwt import current_user
from flask_mongoengine import ValidationError
from flask_mail import Message

from MookAPI.auth import jwt_required
from MookAPI.helpers import is_local
from MookAPI.services import users, user_credentials, misc_activities

import activity

from . import route

bp = Blueprint('users', __name__, url_prefix="/users")

@route(bp, "/current", methods=['GET', 'PATCH'])
@jwt_required()
def current_user_info():
    creds = current_user._get_current_object()
    user = current_user.user

    if request.method == 'GET':
        return jsonify(
            data=user,
            username=creds.username,
            courses_info=user.courses_info()
        )

    elif request.method == 'PATCH':

        data = request.get_json()
        user.full_name = data['full_name']
        user.email = data['email']
        try:
            user.save()
        except ValidationError as e:
            message = "Could not update user: %s" % e.message
            return jsonify(
                error=message
            ), 400

        return user

@route(bp, "/current/password", methods=['PATCH'])
@jwt_required()
def current_user_change_password():
    creds = current_user._get_current_object()

    if request.method == 'PATCH':

        data = request.get_json()
        if not creds.verify_pass(data['current_password']):
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

        creds.password = user_credentials.__model__.hash_pass(new_password)
        try:
            creds.save(validate=False) # FIXME This is related to the MongoEngine bug.
        except ValidationError as e:
            response = {
                "error": "Could not update user",
                "message": e.message
            }
            return jsonify(response), 400

        return creds


@route(bp, "/reset_password", methods=['POST'])
def user_reset_password():

    if is_local():
        return jsonify(
            error="Cannot reset password on a local server",
            code=1
        ), 400

    data = request.get_json()
    email = data['email']
    username = data['username']

    try:
        user = users.get(email=email)
    except:
        return jsonify(
            error="There is no user with this email address",
            code=2
        ), 404
    else:
        try:
            creds = user_credentials.get(user=user, username=username, local_server=None)
        except:
            return jsonify(
                error="The username does not match the email address",
                code=3
            ), 400
        else:
            pwd_length = 8
            new_password = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(pwd_length))
            creds.password = user_credentials.__model__.hash_pass(new_password)
            try:
                creds.save(validate=False) # FIXME This is related to the MongoEngine bug.
            except ValidationError as e:
                response = {
                    "error": "Could not update user",
                    "message": e.message
                }
                return jsonify(response), 400
            else:
                body = u"""Bonjour, voici vos nouveaux identifiants pour accéder à la plateforme :
    Nom d'utilisateur : %s
    Mot de passe : %s
Pensez à changer de mot de passe lors de votre prochaine connexion !
À bientôt sur %s !""" % (username, new_password, current_app.config.get("APP_TITLE", "la plateforme"))
                subject = u"Réinitialisation du mot de passe"
                app_title = current_app.config.get("APP_TITLE", None)
                if app_title:
                    subject = "[%s] %s" % (app_title, subject)
                sender = current_app.config["EMAIL_FROM"]

                msg = Message(
                    subject=subject,
                    recipients=[email],
                    body=body,
                    sender=sender
                )

                from ._mail import mail
                mail.send(msg)

                return '', 204 # 204 = "No Content"


@route(bp, "/current/dashboard")
@jwt_required()
def current_user_dashboard():
    creds = current_user._get_current_object()
    user = current_user.user

    return jsonify(
        data=user,
        username=creds.username,
        courses_info=user.courses_info(analytics=True)
    )


@route(bp, "/<user_id>")
# @jwt_required()
def get_user_info(user_id):
    return users.get_or_404(user_id)

@route(bp, "/<user_id>/dashboard")
@jwt_required()
def user_dashboard(user_id):
    user = users.get_or_404(user_id)

    return jsonify(
        data=user,
        courses_info=user.courses_info(analytics=True)
    )


@route(bp, "/register", methods=['POST'])
def register_user():
    """Registers a new user"""
    misc_activities.create(type="register_user_attempt")

    # First, check that if this is a local server, it "knows itself":
    from MookAPI.helpers import is_local, current_local_server
    local_server = current_local_server()
    if is_local() and not local_server:
        response = {
            "error":"The local server could not find its document",
            "code":7
        }
        return jsonify(response), 500


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

    except Exception as e:
        response = {
            "error": "Unrecognized exception",
            "message": e.message,
            "code": 1
        }
        return jsonify(response), 400

    else:

        try:
            creds = user_credentials.create(
                user=new_user,
                username=username,
                password=password,
                local_server=local_server
            )
            ## Password is automatically hashed in the Service.

        except NotUniqueError as e:
            new_user.delete()
            response = {
                "error": "This username already belongs to someone",
                "message": e.message,
                "code": 3
            }
            return jsonify(response), 400

        else:

            if local_server:
                local_server.synced_users.append(new_user)
                local_server.clean()
                local_server.save(validate=False) # FIXME Do validation when MongoEngine bug is fixed.

            misc_activities.create(
                credentials=creds,
                type="register_user_attempt",
                object_title="success"
            )
            return new_user, 201

@route(bp, "/phagocyte", methods=['POST'])
@jwt_required()
def absorb_user():
    data = request.get_json()
    try:
        local_server = ObjectId(data.get('local_server', None))
    except:
        local_server = None

    username = data.get('username', None)
    password = data.get('password', None)

    try:
        creds = user_credentials.get(
            local_server=local_server,
            username=username,
            password=password
        )
    except DoesNotExist as e:
        return jsonify(
            code=1,
            error=e.message
        ), 404
    except Exception as e:
        return jsonify(
            code=2,
            error=e.message
        ), 500
    else:
        user = current_user.user
        try:
            user.phagocyte(
                other=creds.user,
                self_credentials=current_user._get_current_object()
            )
        except Exception as e:
            return jsonify(
                code=3,
                error=e.message
            ), 500
        else:
            return user

@route(bp, "/credentials/<credentials_id>")
def get_user_credentials(credentials_id):
    return user_credentials.get_or_404(id=credentials_id)
