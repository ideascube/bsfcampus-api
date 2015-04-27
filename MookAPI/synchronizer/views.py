import flask
import documents
import json
import datetime
from . import bp
from bson import json_util
from MookAPI import app_config
import requests
from requests.auth import AuthBase

def pile_update_items(array):
	print len(array), "items to update:"

def pile_delete_items(array):
	print len(array), "items to delete:"

def pile_items(json):
	pile_update_items(json['items']['update'])
	pile_delete_items(json['items']['delete'])


@bp.route("/fetch_list")
def get_fetch_list():
	api_host = app_config.central_server_api_host
	url = api_host + 'local_servers/sync'
	email = app_config.central_server_api_key
	password = app_config.central_server_api_secret
	
	r = requests.get(url, auth=(email, password))

	if r.status_code == 200:

		pile_items(r.json())

		return flask.Response(
			response=json_util.dumps({'error': 0}),
			mimetype='application/json'
			)

	else:
		json = {
			'error': 1,
			'response_code': r.status_code,
		}
		return flask.Response(
			response=json_util.dumps(json),
			mimetype='application/json'
			)
