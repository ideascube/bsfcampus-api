import flask
import documents
import json
import datetime
from . import bp
import bson
from MookAPI import app_config
import requests
import exceptions
import sys

##FIXME Do something better here.
document_module_names = [
	"MookAPI.hierarchy.documents",
	"MookAPI.resources.documents",
	"MookAPI.resources.documents.audio",
	"MookAPI.resources.documents.downloadable_file",
	"MookAPI.resources.documents.exercise",
	"MookAPI.resources.documents.external_video",
	"MookAPI.resources.documents.rich_text",
	"MookAPI.resources.documents.video",
	]
def import_module(module_name):
	return __import__(module_name, fromlist=[''])
document_modules = map(import_module, document_module_names)

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
			response=bson.json_util.dumps({
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
			response=bson.json_util.dumps(json),
			mimetype='application/json'
			)

def create_object(document_class, url):

	r = requests.get(url)
	
	if r.status_code == 200:
		try:
			bson_object = bson.json_util.loads(r.text)
			obj = document_class.init_with_json_result(bson_object)
		except:
			return None, str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])

		return obj, None

	message = "Could not fetch info, got status code " + str(r.status_code)
	return None, message


def update_item(item):
	for module in document_modules:

		if hasattr(module, item.class_name):
			document_class = getattr(module, item.class_name)
			local_objects = document_class.objects(distant_id=item.distant_id)

			if len(local_objects) > 1:
				return False, "There were at least two objects with that distant_id."

			##FIXME Right now, a new object is always created.
			## We need to update the existing object if there is one.
			new_object, message = create_object(document_class, item.url)

			if new_object is None:
				message = "Could not create new object: " + message
				return False, message

			new_object.save()
			return True, None

	return False, "Document class name not recognized"

def delete_item(item):
	for module in document_modules:
		if hasattr(module, item.class_name):
			document_class = getattr(module, item.class_name)
			local_objects = document_class.objects(distant_id=item.distant_id)

			if len(local_objects) == 1:
				local_object = local_objects.first()
				local_object.delete()
				return True, None

			else:
				return False, "There was not exactly one item to delete"

	return False, "Document class name not recognized"

@bp.route("/depile_item")
def depile_sync_item():
	item = documents.ItemToSync.objects.order_by('queue_position').first()

	if item is None:
		return flask.Response(
			response=bson.json_util.dumps({
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
				response=bson.json_util.dumps({'error': 0, 'changes_made': 1, 'updates_made': 1}),
				mimetype='application/json'
				)
		else:
			item.errors.append(str(result[1]))
			item.save()
			return flask.Response(
				response=bson.json_util.dumps({'error': 1, 'changes_made': 0, 'error_details': result[1]}),
				mimetype='application/json'
				)

	elif item.action == 'delete':
		result = delete_item(item)
		if result[0]:
			item.delete()
			return flask.Response(
				response=bson.json_util.dumps({'error': 0, 'changes_made': 1, 'deletes_made': 1}),
				mimetype='application/json'
				)
		else:
			item.errors.append(str(result[1]))
			item.save()
			return flask.Response(
				response=bson.json_util.dumps({'error': 1, 'changes_made': 0, 'error_details': result[1]}),
				mimetype='application/json'
				)
