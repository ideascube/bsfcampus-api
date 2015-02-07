from flask import Flask
from flask.ext.mongoengine import MongoEngine
from flask.ext.admin import Admin
from flask.ext.admin.contrib.mongoengine import ModelView
import flask_cors


### CREATE FLASK APP
app = Flask(__name__)
app.config["SECRET_KEY"] = "cj3ff02m617k3WxO703dYke088HcU94R"


### SETUP DATABASE
app.config["MONGODB_SETTINGS"] = {'DB': "mookbsf"}
db = MongoEngine(app)


### ALLOW CROSS DOMAIN REQUESTS
cors = flask_cors.CORS(app, resources={r"/*": {"origins": "*"}})


### LOAD APP-LEVEL MODULES
## Views: define HTTP endpoints
import views


### LOAD BLUEPRINTS
## Resources
import resources
app.register_blueprint(resources.bp, url_prefix="/resources")
## Tracks
import tracks
app.register_blueprint(tracks.bp, url_prefix="/tracks")


### ADMINISTRATION INTERFACE
admin = Admin(app)
admin.add_view(ModelView(resources.documents.Resource))
admin.add_view(ModelView(tracks.documents.Track))