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
	admin.add_view(ModelView(resources.documents.exercise.ExerciseResource, name='Exercise', category='Resources'))
	## Rich text resources
	import resources.documents.rich_text
	admin.add_view(ModelView(resources.documents.rich_text.RichTextResource, name='Rich Text', category='Resources'))
	## External video resources
	import resources.documents.external_video
	admin.add_view(ModelView(resources.documents.external_video.ExternalVideoResource, name='External Video', category='Resources'))
	## Audio resources
	import resources.documents.audio
	admin.add_view(ModelView(resources.documents.audio.AudioResource, name='Audio', category='Resources'))
	## Video resources
	import resources.documents.video
	admin.add_view(ModelView(resources.documents.video.VideoResource, name='Video', category='Resources'))
	## Downloadable file resources
	import resources.documents.downloadable_file
	admin.add_view(ModelView(resources.documents.downloadable_file.DownloadableFileResource, name='Downloadable File', category='Resources'))
	## Tracks
	import hierarchy.documents as hierarchy_documents
	admin.add_view(ModelView(hierarchy_documents.Track, name='Track', category='Hierarchy'))
	admin.add_view(ModelView(hierarchy_documents.Skill, name='Skill', category='Hierarchy'))
	admin.add_view(ModelView(hierarchy_documents.Lesson, name='Lesson', category='Hierarchy'))
	# ## Config
	# import config.documents
	# admin.add_view(ModelView(config.documents.ConfigParameters))

create_admin_interface()
