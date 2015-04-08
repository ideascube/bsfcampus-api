from flask import Flask
from flask.ext.mongoengine import MongoEngine
from flask.ext.admin import Admin
from flask.ext.admin.contrib.mongoengine import ModelView
from flask_cors import CORS
import app_config

### CREATE FLASK APP
app = Flask(__name__)
app.config["SECRET_KEY"] = "cj3ff02m617k3WxO703dYke088HcU94R"


### SETUP DATABASE
app.config["MONGODB_SETTINGS"] = {'DB': "mookbsf"}
db = MongoEngine(app)


### GLOBAL PARAMETERS
## FIXME: These should come from the 'config' collection in the DB.
params = {
	'NUMBER_OF_QUESTIONS': 10,
	'MAX_NUMBER_MISTAKES': 3,
	'MAX_SHARE_MISTAKES': 1/3,
}


### ALLOW CROSS DOMAIN REQUESTS
cors = CORS(app, resources={r"/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'


### CENTRAL-SERVER-ONLY AND LOCAL-SERVER-ONLY DECORATORS
## Central-server-only
def if_central(func):
	if app_config.server_type == 'central':
		return func
	else:
		def empty_function(*args, **kwargs):
			pass
		return empty_function

## Local-server-only
def if_local(func):
	if app_config.server_type == 'local':
		return func
	else:
		def empty_function(*args, **kwargs):
			pass
		return empty_function


### LOAD APP-LEVEL MODULES
## Views: define HTTP endpoints
import views


### LOAD BLUEPRINTS
## Resources
import resources
app.register_blueprint(resources.bp, url_prefix="/resources")
## Hierarchy
import hierarchy
app.register_blueprint(hierarchy.bp, url_prefix="/hierarchy")
## Activity
import activity
app.register_blueprint(activity.bp, url_prefix="/activity")
## Config
import config
app.register_blueprint(config.bp, url_prefix="/config")

### ADMINISTRATION INTERFACE
@if_central
def create_admin_interface():
	admin = Admin(app)
	## Exercise resources
	import resources.documents.exercise
	admin.add_view(ModelView(resources.documents.exercise.ExerciseResource))
	## Rich text resources
	import resources.documents.rich_text
	admin.add_view(ModelView(resources.documents.rich_text.RichTextResource))
	## External video resources
	import resources.documents.external_video
	admin.add_view(ModelView(resources.documents.external_video.ExternalVideoResource))
	## Audio resources
	import resources.documents.audio
	admin.add_view(ModelView(resources.documents.audio.AudioResource))
	## Video resources
	import resources.documents.video
	admin.add_view(ModelView(resources.documents.video.VideoResource))
	## Downloadable file resources
	import resources.documents.downloadable_file
	admin.add_view(ModelView(resources.documents.downloadable_file.DownloadableFileResource))
	## Tracks
	import hierarchy.documents as hierarchy_documents
	admin.add_view(ModelView(hierarchy_documents.Track))
	admin.add_view(ModelView(hierarchy_documents.Skill))
	admin.add_view(ModelView(hierarchy_documents.Lesson))
	## Config
	import config.documents
	admin.add_view(ModelView(config.documents.ConfigParameters))

create_admin_interface()
