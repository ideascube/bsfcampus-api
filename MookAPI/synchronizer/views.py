import sys
import requests
import bson

import flask
from flask.ext import restful

from MookAPI import app_config, api
import documents

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

central_api_host = app_config.central_server_api_host

class LocalServerResetView(restful.Resource):

    def get(self):
        url = central_api_host + 'local_servers/reset'
        email = app_config.central_server_api_key
        password = app_config.central_server_api_secret
        
        r = requests.get(url, auth=(email, password))

        if r.status_code == 200:
            return {
                'error': 0
            }

        else:
            return {
                'error': 1,
                'response_code': r.status_code
            }

api.add_resource(LocalServerResetView, '/synchronizer/reset', endpoint='local_server_reset')


class LocalServerFetchListView(restful.Resource):

    def _pile_update_items(self, array):
        for item in array:
            item_document = documents.ItemToSync(
                action='update',
                url=item['url'],
                distant_id=item['_ref']['$id']['$oid'],
                class_name=item['_cls'],
                )
            item_document.save()

    def _pile_delete_items(self, array):
        for item in array:
            item_document = documents.ItemToSync(
                action='delete',
                distant_id=item['_ref']['$id']['$oid'],
                class_name=item['_cls']
                )
            item_document.save()

    def _pile_items(self, json):
        items = json['items']
        updates = self._pile_update_items(items['update'])
        deletes = self._pile_delete_items(items['delete'])
        return len(items['update']), len(items['delete'])

    def get(self):

        url = central_api_host + 'local_servers/sync'
        email = app_config.central_server_api_key
        password = app_config.central_server_api_secret
        
        r = requests.get(url, auth=(email, password))
        ## Synchronous!

        if r.status_code == 200:

            new_updates, new_deletes = self._pile_items(r.json())

            return {
                'error': 0,
                'new_updates': new_updates,
                'new_deletes': new_deletes,
            }

        else:

            return {
                'error': 1,
                'response_code': r.status_code,
                'response_message': r.reason
            }

api.add_resource(LocalServerFetchListView, '/synchronizer/fetch_list', endpoint='local_server_fetch_list')

class LocalServerDepileItemView(restful.Resource):

    def _update_object(self, document_class, url, existing_object):

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


    def _update_item(self, item):
        for module in document_modules:

            if hasattr(module, item.class_name):
                document_class = getattr(module, item.class_name)
                local_objects = document_class.objects(distant_id=item.distant_id)

                if len(local_objects) > 1:
                    return False, "There were at least two objects with that distant_id."

                local_object = local_objects.first() # None if object is new.

                updated_object, message = self._update_object(document_class, item.url, local_object)

                if updated_object is None:
                    message = "Could not create new object: " + message
                    return False, message

                updated_object.save()
                return True, None

        return False, "Document class name not recognized"

    def _delete_item(self, item):
        for module in document_modules:
            if hasattr(module, item.class_name):
                document_class = getattr(module, item.class_name)
                local_objects = document_class.objects(distant_id=item.distant_id)

                local_object = local_objects.first()
                if local_object:
                    local_object.delete()
                    return True, None
                else:
                    return False, "There was not exactly one item to delete"

        return False, "Document class name not recognized"

    def get(self):

        item = documents.ItemToSync.objects.order_by('queue_position').first()

        if item is None:
            return {
                'error': 1,
                'changes_made': 0,
                'error_details': 'No more item to depile'
            }

        if item.action == 'update':
            result = self._update_item(item)
            if result[0]:
                item.delete()
                return {
                    'error': 0,
                    'changes_made': 1,
                    'updates_made': 1
                }
            else:
                item.errors.append(str(result[1]))
                item.save()
                return {
                    'error': 1,
                    'changes_made': 0,
                    'error_details': result[1]
                }

        elif item.action == 'delete':
            result = self._delete_item(item)
            if result[0]:
                item.delete()
                return {
                    'error': 0,
                    'changes_made': 1,
                    'deletes_made': 1
                }
            else:
                item.errors.append(str(result[1]))
                item.save()
                return {
                    'error': 1,
                    'changes_made': 0,
                    'error_details': result[1]
                }

api.add_resource(LocalServerDepileItemView, '/synchronizer/depile_item', endpoint='local_server_depile_item')
