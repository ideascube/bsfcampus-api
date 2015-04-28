import flask
import documents
import json
import datetime
from . import bp
from bson import json_util
from MookAPI import app_config
import requests
from requests.auth import AuthBase

import MookAPI.hierarchy.documents
import MookAPI.resources.documents
document_modules = [
	MookAPI.hierarchy.documents,
	MookAPI.resources.documents,
	]

def pile_update_items(array):
	for item in array:
		item_document = documents.ItemToSync(
			action='update',
			url=item['url'],
			distant_id=item['_ref']['$id']['$oid'],
			class_name=item['_cls'],
			)
		item_document.save()

def pile_delete_items(array):
	for item in array:
		item_document = documents.ItemToSync(
			action='delete',
			distant_id=item['_ref']['$id']['$oid'],
			class_name=item['_cls']
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

def hydrate_object(obj, document_class, url):

	r = requests.get(url)
	
	if r.status_code == 200:
		obj.hydrate_with_json(r.json())
		return obj

	return None


def update_item(item):
	print "Updating", item.class_name
	
	for module in document_modules:

		if hasattr(module, item.class_name):
			document_class = getattr(module, item.class_name)
			local_objects = document_class.objects(distant_id=item.distant_id)

			if len(local_objects) > 1:
				return False, "There were at least two objects with that distant_id."

			if len(local_objects) == 0:
				local_object = document_class(distant_id=item.distant_id)
			else:
				local_object = local_objects.first()

			local_object = hydrate_object(local_object, document_class, item.url)

			if local_object is None:
				return False, "Could not hydrate object"

			local_object.save()
			return True, None

	return False, "Document class name not recognized"

def delete_item(item):
	print "Deleting", item.class_name

	for module in document_modules:
		if hasattr(module, item.class_name):
			document_class = getattr(module, item.class_name)
			local_objects = document_class.objects()

			if len(local_objects) == 1:
				local_object = local_objects.first()
				local_object.delete()
				return True, None

			else:
				return False, "There was not exactly one item to delete"

	return False, "Document class name not recognized"

@bp.route("/depile_item")
def depile_sync_item():
	item = documents.ItemToSync.objects.first()

	if item is None:
		return flask.Response(
			response=json_util.dumps({
				'error': 1,
				'changes_made': 0,
				'error_details': 'No more item to depile'}),
			mimetype='application/json'
			)

	if item.action == 'update':
		result = update_item(item)
		if result[0]:
			item.delete()
			return flask.Response(
				response=json_util.dumps({'error': 0, 'changes_made': 1, 'updates_made': 1}),
				mimetype='application/json'
				)
		else:
			item.errors.append(str(result[1]))
			item.save()
			return flask.Response(
				response=json_util.dumps({'error': 1, 'changes_made': 0, 'error_details': result[1]}),
				mimetype='application/json'
				)

	elif item.action == 'delete':
		result = delete_item(item)
		if result[0]:
			item.delete()
			return flask.Response(
				response=json_util.dumps({'error': 0, 'changes_made': 1, 'deletes_made': 1}),
				mimetype='application/json'
				)
		else:
			item.errors.append(str(result[1]))
			item.save()
			return flask.Response(
				response=json_util.dumps({'error': 1, 'changes_made': 0, 'error_details': result[1]}),
				mimetype='application/json'
				)
