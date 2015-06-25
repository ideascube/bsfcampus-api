from mongoengine import NotUniqueError

from flask_jwt import jwt_required, current_user
from flask_restful import Resource, reqparse
from flask_mongoengine import ValidationError

from MookAPI import api
from MookAPI.hierarchy.documents.track import Track
import documents

class CurrentUserView(Resource):

    @jwt_required()
    def get(self):
        """Get the current logged in user data"""

        return current_user._get_current_object()

    @jwt_required()
    def put(self):

        parser = reqparse.RequestParser()
        parser.add_argument('full_name', required=True, type=unicode)
        parser.add_argument('email', required=True, type=unicode)
        args = parser.parse_args()

        user = current_user._get_current_object()

        user.full_name = args.full_name
        user.email = args.email
        try:
            user.save()
        except ValidationError as e:
            response = {
                "error": "Could not update user",
                "message": e.message
            }
            return response, 400

        return user

api.add_resource(CurrentUserView, '/users/current', endpoint='current_user')

class CurrentUserDashboardView(Resource):

    @jwt_required
    def get(self):
        """Get the current logged in user data to display in the dashboard"""

        response = {}
        response.dashboard = {}
        response.dashboard.user = current_user._get_current_object()

        response.dashboard.tracks = []
        for track in Track.objects:
            response.dashboard.tracks.append(track.encode_mongo_for_dashboard(response.dashboard.user))

        return response

api.add_resource(CurrentUserDashboardView, '/users/current/dashboard', endpoint='current_user_dashboard')

class UserView(Resource):

    def get(self, user_id):
        """Get the user data defined by the given user_id"""

        return documents.User.get_unique_object_or_404(user_id)

api.add_resource(UserView, '/users/<user_id>', endpoint='user')

class UserRegisterView(Resource):

    def post(self):
        """Registers a new user"""

        parser = reqparse.RequestParser()
        parser.add_argument('full_name', required=True, type=unicode)
        parser.add_argument('username', required=True, type=unicode)
        parser.add_argument('email', required=True, type=unicode)
        parser.add_argument('password', required=True, type=unicode)
        parser.add_argument('password_confirm', required=True, type=unicode)
        parser.add_argument('accept_cgu', required=True, type=bool)
        args = parser.parse_args()

        if args.password != args.password_confirm:
            response = {
                "error": "Passwords don't match"
            }
            return response, 400

        new_user = documents.User()
        new_user.full_name = args.full_name
        new_user.username = args.username
        new_user.email = args.email
        new_user.password = new_user.hash_pass(args.password)
        new_user.accept_cgu = args.accept_cgu

        try:
            new_user.save()
        except ValidationError as e:
            response = {
                "error": "Could not create user",
                "message": e.message,
                "code": 2
            }
            return response, 400
        except NotUniqueError as e:
            response = {
                "error": "This username already belongs to someone",
                "message": e.message,
                "code": 3
            }
            return response, 400
        except Exception as e:
            response = {
                "error": "Unrecognized exception",
                "message": e.message,
                "code": 1
            }
            return response, 400
        else:
            return new_user

api.add_resource(UserRegisterView, '/register', endpoint='register')

class UserDashboardView(Resource):

    @jwt_required
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
