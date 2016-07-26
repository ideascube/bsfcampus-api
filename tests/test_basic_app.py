
import pytest
import json


def test_app(app):
    assert True


def test_login_fail_with_wrong_authent(client):
    rv = client.post('/auth',
                     content_type='application/json',
                     data=json.dumps({'username': 'joe', 'password': 'pass'}))
    assert rv.status_code == 400


def test_login_succeed_authent(client):
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
    assert rv.status_code == 200


def test_fail_with_wrong_authent(client):
    rv = client.get('/users/current')
    assert rv.status_code == 401


def test_succed_with_right_authent(conn_client):
    rv = conn_client.get('/users/current')
    assert rv.status_code == 200
