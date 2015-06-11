import flask
import documents
import json
from . import bp
from MookAPI import api
from flask.ext.security import login_required
from flask_restful import Resource, reqparse
import flask.ext.security as security
from flask_mongoengine import ValidationError

class CurrentUserView(Resource):

    def get(self):
        """Get the current logged in user data"""
        print ("get current user")

        if not security.current_user.id:
            response = {"status_code": 401}
            return response

        current_user_id = security.current_user.id
        print (current_user_id)
        return documents.User.get_unique_object_or_404(current_user_id)

    @login_required
    def post(self):
        print ("current user post")
        parser = reqparse.RequestParser()
        parser.add_argument('full_name', required=True, type=unicode)
        parser.add_argument('email', required=True, type=unicode)
        args = parser.parse_args()
        if security.current_user.id:
            security.current_user.full_name = args.full_name
            security.current_user.email = args.email
            try:
                security.current_user.save()
            except ValidationError as e:
                response = {"status_code": 400, "message": e.message}
                return response

            current_user_id = security.current_user.id
            return documents.User.get_unique_object_or_404(current_user_id)
        else:
            response = {"status_code": 404}
            return response

api.add_resource(CurrentUserView, '/users/current', endpoint='current_user')


class UserView(Resource):

    def get(self, user_id):
        """Get the user data defined by the given user_id"""
        print ("get user " + user_id)
        return documents.User.get_unique_object_or_404(user_id)

api.add_resource(UserView, '/users/<user_id>', endpoint='user')


class LogoutCurrentUserView(Resource):

    @login_required
    def post(self):
        """Logs out the current user"""
        security.logout_user()

api.add_resource(LogoutCurrentUserView, '/users/logout', endpoint='logout_user')
