from flask import Flask, abort
from flask import make_response
from flask.ext.restful import Api
from flask.ext.mongoengine import MongoEngine
from flask.ext.admin import Admin
from flask.ext.admin.contrib.mongoengine import ModelView
from flask_cors import CORS
from flask_jwt import JWT
import app_config
import datetime
from bson import json_util

### CREATE FLASK APP
app = Flask(__name__)
app.config["SECRET_KEY"] = app_config.app_secret

### SETUP DATABASE
mongodb_settings = {}
mongodb_settings['DB'] = getattr(app_config, 'mongodb_db', 'mookbsf')
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
cors = CORS(app, resources={r"/*": {"origins": app_config.allow_origins}}, supports_credentials=True,
            allow_headers='Content-Type')
app.config['CORS_HEADERS'] = 'Content-Type'


### USERS
## Documents
import users

app.register_blueprint(users.bp, url_prefix="/users")

app.config['JWT_EXPIRATION_DELTA'] = datetime.timedelta(hours=2)
jwt = JWT(app)

@jwt.authentication_handler
def authenticate(username, password):
    try:
        user = users.documents.User.objects.get(username=username)
        #TODO: Check password!
    except:
        return None
    else:
        return user

@jwt.payload_handler
def make_payload(user):
    return {
        'user_id': str(user.id)
    }

@jwt.user_handler
def load_user(payload):
    user_id = payload['user_id']
    try:
        user = users.documents.User.objects.get(id=user_id)
    except:
        return None
    else:
        return user

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
        func()
    return func

## Local-server-only
def if_local(func):
    if server_is_local():
        func()
    return func

## Execute the decorated function no matter what
def execute_always(func):
    func()
    return func

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


@if_local
def import_synchronizer():
    import synchronizer
    app.register_blueprint(synchronizer.bp, url_prefix="/synchronizer")


### ADMINISTRATION INTERFACE
## Eventually this back-office should not exist on the local servers
## To do that, use the @if_central decorator instead of @execute_always
@execute_always
def create_admin_interface():
    admin = Admin(app)

    from admin import ResourceView

    ## Exercise resources
    import resources.documents.exercise

    admin.add_view(ResourceView(resources.documents.exercise.ExerciseResource, name='Exercise', category='Resources'))

    ## Track Validation Tests
    import resources.documents.track_validation

    admin.add_view(ResourceView(resources.documents.track_validation.TrackValidationResource, name='Track Validation Test',
                             category='Resources'))

    ## Rich text resources
    import resources.documents.rich_text

    admin.add_view(ResourceView(resources.documents.rich_text.RichTextResource, name='Rich Text', category='Resources'))

    # No external video on server
    # ## External video resources
    # import resources.documents.external_video
    # admin.add_view(ResourceView(resources.documents.external_video.ExternalVideoResource, name='External Video', category='Resources'))
    # admin.add_view(ModelView(resources.documents.external_video.ExternalVideoResource, name='External Video', category='Resources'))

    ## Audio resources
    import resources.documents.audio
    admin.add_view(ResourceView(resources.documents.audio.AudioResource,
                                                name='Audio',
                                                category='Resources'))
    # admin.add_view(ModelView(resources.documents.audio.AudioResource, name='Audio', category='Resources'))

    ## Video resources
    import resources.documents.video

    admin.add_view(ResourceView(resources.documents.video.VideoResource, name='Video', category='Resources'))

    ## Downloadable file resources
    import resources.documents.downloadable_file
    admin.add_view(ResourceView(resources.documents.downloadable_file.DownloadableFileResource,
                                                name='Downloadable File',
                                                category='Resources'))
    # admin.add_view(ModelView(resources.documents.downloadable_file.DownloadableFileResource, name='Downloadable File',
    #                          category='Resources'))

    ## Hierarchy
    import hierarchy.documents as hierarchy_documents
    from admin import HierarchyTrackView, HierarchySkillView, HierarchyLessonView

    admin.add_view(HierarchyTrackView(hierarchy_documents.track.Track, name='Track', category='Hierarchy'))
    admin.add_view(HierarchySkillView(hierarchy_documents.skill.Skill, name='Skill', category='Hierarchy'))
    admin.add_view(HierarchyLessonView(hierarchy_documents.lesson.Lesson, name='Lesson', category='Hierarchy'))

    # ## Config
    # import config.documents
    # admin.add_view(ModelView(config.documents.ConfigParameters))

    ## Authentication
    from admin import UserView

    admin.add_view(UserView(users.documents.User, name='User', category='Authentication'))
    admin.add_view(ModelView(users.documents.Role, name='Role', category='Authentication'))

    ## Local servers
    import local_servers.documents as local_servers_documents

    admin.add_view(ModelView(local_servers_documents.LocalServer, name='Local server', category='Authentication'))
