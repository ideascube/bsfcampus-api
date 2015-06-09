import flask
import documents
import json
from . import bp
from MookAPI import api
from flask.ext.security import login_required
from flask.ext import restful
import flask.ext.security as security

class UserView(restful.Resource):

    @login_required
    def get(self):
        """Get the current logged in user data"""
        return security.current_user

api.add_resource(UserView, '/users/current', endpoint='current_user')
