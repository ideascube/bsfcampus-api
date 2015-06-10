import flask
import documents
import json
from . import bp
from MookAPI import api
from flask.ext.security import login_required
from flask.ext import restful
import flask.ext.security as security
from flask.ext.security.core import AnonymousUser
from flask_cors import cross_origin

class CurrentUserView(restful.Resource):

    def get(self):
        """Get the current logged in user data"""
        print ("get current user")

        try:
            current_user_id = security.current_user.id
        except:
            response = {"status_code": 401}
            return response
        else:
            print (current_user_id)
            return documents.User.get_unique_object_or_404(current_user_id)

api.add_resource(CurrentUserView, '/users/current', endpoint='current_user')


class UserView(restful.Resource):

    def get(self, user_id):
        """Get the user data defined by the given user_id"""
        print ("get user " + user_id)
        return documents.User.get_unique_object_or_404(user_id)

api.add_resource(UserView, '/users/<user_id>', endpoint='user')


class LogoutCurrentUserView(restful.Resource):

    @login_required
    def post(self):
        """Logs out the current user"""
        security.logout_user()

api.add_resource(LogoutCurrentUserView, '/users/logout', endpoint='logout_user')
