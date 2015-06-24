import flask
import documents
import json
from . import bp
from MookAPI import api
from flask.ext.security import login_required
from flask_restful import Resource, reqparse
import flask.ext.security as security
from flask_mongoengine import ValidationError
from MookAPI.hierarchy.documents.track import Track

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
        """Update the current logged in user data"""
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

class CurrentUserDashboardView(Resource):

    @login_required
    def get(self):
        """Get the current logged in user data to display in the dashboard"""
        current_user_id = security.current_user.id

        response = {}
        response.dashboard = {}
        response.dashboard.user = documents.User.get_unique_object_or_404(current_user_id)

        response.dashboard.tracks = []
        for track in Track.objects:
            response.dashboard.tracks.append(track.encode_mongo_for_dashboard(response.dashboard.user))

        return response

api.add_resource(CurrentUserDashboardView, '/users/current/dashboard', endpoint='current_user_dashboard')

class UserView(Resource):

    def get(self, user_id):
        """Get the user data defined by the given user_id"""
        print ("get user " + user_id)
        return documents.User.get_unique_object_or_404(user_id)

api.add_resource(UserView, '/users/<user_id>', endpoint='user')

class UserDashboardView(Resource):

    @login_required
    def get(self, user_id):
        """Get the user data to display in the dashboard"""

        response = {'dashboard': {}}
        response['dashboard']['user'] = documents.User.get_unique_object_or_404(user_id)

        response['dashboard']['tracks'] = []
        for track in Track.objects:
            response['dashboard']['tracks'].append(track.encode_mongo_for_dashboard(response['dashboard']['user']))
        response['dashboard']['tracks'].sort(key=lambda t: t['order'])

        return response

api.add_resource(UserDashboardView, '/users/<user_id>/dashboard', endpoint='user_dashboard')

class LogoutCurrentUserView(Resource):

    @login_required
    def post(self):
        """Logs out the current user"""
        security.logout_user()

api.add_resource(LogoutCurrentUserView, '/users/logout', endpoint='logout_user')
