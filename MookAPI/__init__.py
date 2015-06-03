from flask import Flask
from flask import make_response
from flask.ext.restful import Api
from flask.ext.mongoengine import MongoEngine
from flask.ext.admin import Admin
from flask.ext.admin.contrib.mongoengine import ModelView
from flask.ext.security import Security, MongoEngineUserDatastore
from flask_cors import CORS
import app_config
import base64
from bson import json_util

### CREATE FLASK APP
app = Flask(__name__)
app.config["SECRET_KEY"] = app_config.app_secret

### SETUP DATABASE
mongodb_settings = {}
if hasattr(app_config, 'mongodb_db'):
    mongodb_settings['DB'] = app_config.mongodb_db
else:
    mongodb_settings['DB'] = 'mookbsf'
if hasattr(app_config, 'mongodb_host'):
    mongodb_settings['HOST'] = app_config.mongodb_host
if hasattr(app_config, 'mongodb_port'):
    mongodb_settings['port'] = app_config.mongodb_port
if hasattr(app_config, 'mongodb_username'):
    mongodb_settings['username'] = app_config.mongodb_username
if hasattr(app_config, 'mongodb_password'):
    mongodb_settings['password'] = app_config.mongodb_password
app.config["MONGODB_SETTINGS"] = mongodb_settings
db = MongoEngine(app)

import mongo_coder as mc

### INITIATE API
api = Api(app)


@api.representation('application/json')
def output_json(data, code, headers=None):
    if isinstance(data, mc.MongoCoderDocument):
        document = data.encode_mongo()
        json_envelope = data.__class__.json_key()
        data = {json_envelope: document}

    elif isinstance(data, db.QuerySet):
        if issubclass(data._document, mc.MongoCoderDocument):
            documents = map(lambda d: d.encode_mongo(), data)
            json_envelope = data._document.json_key_collection()
            data = {json_envelope: documents}

    resp = make_response(json_util.dumps(data), code)
    resp.headers.extend(headers or {})
    return resp


### ALLOW CROSS DOMAIN REQUESTS
cors = CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
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
## Header authentication
@security.login_manager.request_loader
def load_user_from_request(request):
    auth_key = request.headers.get('Authorization')
    if auth_key:
        auth_key = auth_key.replace('Basic ', '', 1)
        try:
            auth_key = base64.b64decode(auth_key)
        except TypeError:
            pass
        email, password = auth_key.split(":", 1)
        user = users.documents.User.objects.get(email=email)  # , password=password)
        if user:
            return user
    return None


### CENTRAL-SERVER-ONLY AND LOCAL-SERVER-ONLY DECORATORS
## Server is central unless specified otherwise.
def server_is_local():
    if hasattr(app_config, 'server_type'):
        return app_config.server_type.lower() == 'local'
    return False


def server_is_central():
    return not server_is_local()


## Central-server-only
def if_central(func):
    if server_is_central():
        return func
    else:
        def empty_function(*args, **kwargs):
            pass

        return empty_function


## Local-server-only
def if_local(func):
    if server_is_local():
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
def import_local_servers():
    import local_servers

    app.register_blueprint(local_servers.bp, url_prefix="/local_servers")


import_local_servers()


@if_local
def import_synchronizer():
    import synchronizer

    app.register_blueprint(synchronizer.bp, url_prefix="/synchronizer")


import_synchronizer()


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

    admin.add_view(ModelView(resources.documents.downloadable_file.DownloadableFileResource, name='Downloadable File',
                             category='Resources'))
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
    import local_servers.documents as local_servers_documents

    admin.add_view(ModelView(local_servers_documents.LocalServer, name='Local server', category='Authentication'))

create_admin_interface()