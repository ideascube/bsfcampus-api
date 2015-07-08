import sys
import requests
import bson

from flask import Blueprint, jsonify, current_app

from MookAPI.services import items_to_sync
from . import route

bp = Blueprint("synchronizer", __name__, url_prefix="/synchronizer")

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

@route(bp, "/reset")
def reset_sync():
    url = current_app.config['CENTRAL_SERVER_HOST'] + '/local_servers/reset'
    key = current_app.config['CENTRAL_SERVER_KEY']
    secret = current_app.config['CENTRAL_SERVER_SECRET']

    r = requests.get(url, auth=(key, secret))

    if r.status_code == 200:
        return jsonify(error=0)

    else:
        return jsonify(error=1), r.status_code

@route(bp, "/fetch_list")
def fetch_sync_list():
    def _pile_update_items(array):
        for item in array:
            items_to_sync.create(
                action='update',
                url=item['url'],
                distant_id=item['_id']['$oid'],
                class_name=item['_cls'],
                )

    def _pile_delete_items(array):
        for item in array:
            items_to_sync.create(
                action='delete',
                distant_id=item['_ref']['$id']['$oid'],
                class_name=item['_cls']
                )

    def _pile_items(json):
        items = json['items']
        _pile_update_items(items['update'])
        _pile_delete_items(items['delete'])
        return len(items['update']), len(items['delete'])

    url = current_app.config['CENTRAL_SERVER_HOST'] + '/local_servers/sync'
    key = current_app.config['CENTRAL_SERVER_KEY']
    secret = current_app.config['CENTRAL_SERVER_SECRET']

    r = requests.get(url, auth=(key, secret))
    ## Synchronous!

    if r.status_code == 200:

        new_updates, new_deletes = _pile_items(r.json())

        return jsonify(error=0, new_updates=new_updates, new_deletes=new_deletes)

    else:

        return jsonify(error= 1, message= r.reason), r.status_code


@route(bp, "/depile_item")
def depile_sync_item():

    def _update_object(document_class, url, existing_object):

        r = requests.get(url)
        
        if r.status_code == 200:
            try:
                bson_object = bson.json_util.loads(r.text)
                obj = document_class.decode_json_result(bson_object)
                if existing_object:
                    obj.id = existing_object.id
            except:
                return None, str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])

            return obj, None

        message = "Could not fetch info, got status code " + str(r.status_code)
        return None, message


    def _update_item(item):
        item_class_name = item.class_name.split('.')[-1]
        print (item_class_name)
        for module in document_modules:
            if hasattr(module, item_class_name):
                document_class = getattr(module, item_class_name)
                local_objects = document_class.objects(distant_id=item.distant_id)

                if len(local_objects) > 1:
                    return False, "There were at least two objects with that distant_id."

                local_object = local_objects.first()  # None if object is new.

                updated_object, message = _update_object(document_class, item.url, local_object)

                if updated_object is None:
                    message = "Could not create new object: " + message
                    return False, message

                updated_object.save()
                return True, None

        return False, "Document class name not recognized: " + item_class_name

    def _delete_item(item):
        item_class_name = item.class_name.split('.')[-1]
        print (item_class_name)
        for module in document_modules:
            if hasattr(module, item_class_name):
                document_class = getattr(module, item_class_name)
                local_objects = document_class.objects(distant_id=item.distant_id)

                for local_object in local_objects:
                    local_object.delete()
                return True, None

        return False, "Document class name not recognized: " + item_class_name


    item = items_to_sync.queryset().order_by('queue_position').first()

    if item is None:
        return jsonify(error=1, changes_made=0, error_details="No more items to depile")

    if item.action == 'update':
        result = _update_item(item)
        if result[0]:
            item.delete()
            return jsonify(error=0, changes_made=1, updates_made=1)

        else:
            item.errors.append(str(result[1]))
            item.save()
            return jsonify(error=1, changes_made=0, error_details=result[1])

    elif item.action == 'delete':
        result = _delete_item(item)
        if result[0]:
            item.delete()
            return jsonify(error=0, changes_made=1, deletes_made=1)

        else:
            item.errors.append(str(result[1]))
            item.save()
            return jsonify(error=1, changes_made=0, error_details=result[1])
