from MookAPI.api import create_app
import pytest
import os
import os.path as op
from pymongo import MongoClient
import json
from flask.testing import FlaskClient

def create_config(test_path):
    static_path = op.join(test_path, "static/")
    os.makedirs(static_path)
    class Config(object):
        SECRET_KEY = 'Find a nice secret key to protect the app.' # Use e.g. http://randomkeygen.com/
        MONGODB_DB = 'bsfcampus_test'
        CORS_ORIGINS = ['http://localhost', 'http://localhost:63342']
        UPLOAD_FILES_PATH = static_path
        UPLOAD_FILES_URL = "http://url_to_static/"
        ## Local servers only:
        CENTRAL_SERVER_HOST = 'http://localhost:5000'
        CENTRAL_SERVER_KEY = ''
        CENTRAL_SERVER_SECRET = ''
        ## Central servers
        MAIL_SERVER = 'localhost'
        EMAIL_FROM = ("Name", "email@email.com")
        APP_TITLE = "App Title"
    return Config


class AuthClient(FlaskClient):
    def __init__(self, *args, **kwargs):
        FlaskClient.__init__(self, *args, **kwargs)
        self._auth_token = None

    def open(self, *args, **kwargs):
        if self._auth_token:
            headers = kwargs.get('headers', [])
            headers.append(('Authorization', 'bearer {}'.format(self._auth_token)))
            kwargs['headers'] = headers

        return FlaskClient.open(self, *args, **kwargs)

@pytest.yield_fixture
def app(tmpdir):
    config = create_config(str(tmpdir))
    app = create_app(config)
    app.test_client_class = AuthClient
    yield app
    client = MongoClient()
    client.drop_database('bsfcampus_test')


@pytest.fixture
def conn_client(client):
    from MookAPI.services import users, user_credentials
    user = users.new(
              email=None,
              full_name="Joe Dante",
              country=None,
              occupation=None,
              organization=None,
              accept_cgu=True
          )
    user.save()
    
    creds = user_credentials.create(
                user=user,
                username="joed",
                password="password"
            )
    rv = client.post('/auth',
                     content_type='application/json',
                     data=json.dumps({'username': 'joed', 'password': 'password'}))
    result = json.loads(rv.data)
    client._auth_token = result['token']
    
    return client
