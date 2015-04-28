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
	for item in array:
		item_document = documents.ItemToSync(
			action='update',
			url=item['url'],
			distant_id=item['_ref']['$id']['$oid'],
			className=item['_cls'],
			)
		item_document.save()

def pile_delete_items(array):
	for item in array:
		item_document = documents.ItemToSync(
			action='delete',
			distant_id=item['_ref']['$id']['$oid'],
			className=item['_cls']
			)
		item_document.save()

def pile_items(json):
	items = json['items']
	updates = pile_update_items(items['update'])
	deletes = pile_delete_items(items['delete'])
	return len(items['update']), len(items['delete'])


@bp.route("/fetch_list")
def get_fetch_list():
	api_host = app_config.central_server_api_host
	url = api_host + 'local_servers/sync'
	email = app_config.central_server_api_key
	password = app_config.central_server_api_secret
	
	r = requests.get(url, auth=(email, password))

	if r.status_code == 200:

		new_updates, new_deletes = pile_items(r.json())

		return flask.Response(
			response=json_util.dumps({
				'error': 0,
				'new_updates': new_updates,
				'new_deletes': new_deletes,
				}),
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
