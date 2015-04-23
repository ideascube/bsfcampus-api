from flask import Flask
from flask.ext.mongoengine import MongoEngine
from flask.ext.admin import Admin
from flask.ext.admin.contrib.mongoengine import ModelView
from flask.ext.security import Security, MongoEngineUserDatastore
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

### SECURITY
## Documents
import users, users.documents
app.register_blueprint(users.bp, url_prefix="/users")
## Datastore
user_datastore = MongoEngineUserDatastore(db, users.documents.User, users.documents.Role)
## Configuration
app.config['SECURITY_PASSWORD_HASH'] = 'bcrypt'
app.config['SECURITY_PASSWORD_SALT'] = app_config.password_salt
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
security = Security(
	app, 
	datastore=user_datastore,
	register_blueprint=True
	)


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

## The "local server" module allows to identify local servers on the central server.
## It should only exist on the central server.
## The counterpart on the local servers will be some authentication file.
@if_central
def import_local_server():
	import local_server
	app.register_blueprint(local_server.bp, url_prefix="/sync")
import_local_server()


### ADMINISTRATION INTERFACE
## Eventually this back-office should not exist on the local servers (maybe even on the central server...)
## To do that, uncomment the decorator
# @if_central
def create_admin_interface():
	admin = Admin(app)
	## Exercise resources
	import resources.documents.exercise
	admin.add_view(ModelView(resources.documents.exercise.ExerciseResource, name='Exercise', category='Resources'))
	## Rich text resources
	import resources.documents.rich_text
	admin.add_view(ModelView(resources.documents.rich_text.RichTextResource, name='Rich Text', category='Resources'))
	# No external video on server
	# ## External video resources
	# import resources.documents.external_video
	# admin.add_view(ModelView(resources.documents.external_video.ExternalVideoResource, name='External Video', category='Resources'))
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
	## Authentication
	admin.add_view(ModelView(users.documents.User, name='User', category='Authentication'))
	admin.add_view(ModelView(users.documents.Role, name='Role', category='Authentication'))
	import local_server.documents as local_server_documents
	admin.add_view(ModelView(local_server_documents.LocalServer, name='Local server', category='Authentication'))

create_admin_interface()
