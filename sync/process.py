from bson import json_util
import requests
import time

from documents import SyncTasksService

sync_tasks_service = SyncTasksService()


class SyncProcess(object):

    PATHS = dict(
        reset="/local_servers/reset",
        fetch_list="/local_servers/sync"
    )

    def __init__(self, connector, local_server, **kwargs):
        self.connector = connector
        self.local_server = local_server
        self.should_try_to_resolve_reference = True

    def fetch_sync_list(self):

        print "Fetching new list of operations"

        r = self.connector.get(self.PATHS['fetch_list'])

        if r.status_code == 200:
            print "Response from server is OK."

            data = json_util.loads(r.text)['data']

            updates = []
            deletes = []

            for item in data['updates']:
                db_item = sync_tasks_service.create_update_task(item)
                updates.append(db_item)
                print "* Created task: %s" % db_item

            for item in data['deletes']:
                db_item = sync_tasks_service.create_delete_task(item)
                deletes.append(db_item)
                print "* Created task: %s" % db_item

            if not updates and not deletes:
                print "==> No new task to create"

            return True, dict(updates=updates, deletes=deletes)

        else:

            print "Got error code %d from server" % r.status_code

            return False, dict(
                error=r.reason,
                status_code=r.status_code
            )

    def depile_item(self, item):
        print "Performing action: %s" % item
        try:
            result = item.depile(connector=self.connector)
        except:
            return False
        else:
            self.should_try_to_resolve_reference = True
            return result

    def _post_document(self, document):
        path = "/local_servers/add_item"
        from bson.json_util import dumps, loads
        json = dumps(document.to_json(for_central=True))
        r = self.connector.post(path, json=json)

        if r.status_code == 200:
            response = loads(r.text)
            data = response['data']

            from MookAPI.helpers import get_service_for_class
            service = get_service_for_class(data['_cls'])
            try:
                new_document = service.__model__.from_json(
                    data,
                    from_central=True,
                    overwrite_document=document
                )
                new_document.clean()
                new_document.save(validate=False) # FIXME MongoEngine bug, hopefully be fixed in next version
                print "Overwrote local document with information from central server"
                if service.__class__.__name__ == 'UsersService': # FIXME Do something cleaner
                    self._subscribe_user(new_document)
            except:
                print "An error occurred while overwriting the local document"
        else:
            print "An error occurred on the central server when trying to send the document"

    def _post_documents(self, documents):
        path = "/local_servers/add_items"
        from bson.json_util import dumps, loads
        items = dict()
        for document in documents:
            item = document.to_json(for_central=True)
            items[str(document.id)] = item
        json = dumps(dict(items=items))
        r = self.connector.post(path, json=json)

        if r.status_code == 200:
            response = loads(r.text)
            data = response['data']
            updated_items = data['items']

            from MookAPI.helpers import get_service_for_class
            for local_id, updated_item in updated_items:
                service = get_service_for_class(updated_item['_cls'])
                try:
                    new_document = service.__model__.from_json(
                        data,
                        from_central=True,
                        overwrite_document=items[local_id]
                    )
                    new_document.clean()
                    new_document.save(validate=False) # FIXME MongoEngine bug, hopefully be fixed in next version
                    print "Overwrote local document with information from central server"
                    # if service.__class__.__name__ == 'UsersService':
                    #     self._subscribe_user(new_document) # FIXME Find a good way to do this
                except:
                    print "An error occurred while overwriting the local document"
        else:
            print "An error occurred on the central server when trying to send the document"

    def _post_next_document(self):
        print "Checking if there is a document to post to the central server..."
        if self.local_server:
            self.local_server.reload()
            for user in self.local_server.synced_users:
                for document in user.all_synced_documents(local_server=self.local_server):
                    if not document.central_id:
                        try:
                            print "Sending document: %s" % document
                        except:
                            print "Sending document: [Cannot get representation]"
                        self._post_document(document)
                        return True
            print "No more document to post"
            return False
        print "This local server cannot identify itself (for now)"
        return False

    def post_all_documents(self):
        succeeded = True
        counter = 0
        while succeeded:
            succeeded = self._post_next_document()
            if succeeded:
                counter += 1

        return counter

    def resolve_references(self):
        if self.should_try_to_resolve_reference:
            print "Checking if there are references to resolve"
            from MookAPI.sync import UnresolvedReference
            for unresolved_ref in UnresolvedReference.objects.all():
                unresolved_ref.resolve()
            if self.local_server:
                self.local_server.reload()
            self.should_try_to_resolve_reference = False

    def next_action(self):
        item = sync_tasks_service.get_next_task()

        if item:
            result = self.depile_item(item)
            return 'depile', result

        else:
            print "==> No more item to depile"

            self.resolve_references()
            posted_documents = self.post_all_documents()

            if posted_documents > 0:
                return 'post_local', posted_documents

            result, details = self.fetch_sync_list()
            return 'fetch_list', result, details

    def run(self, interval=None):

        if not interval:
            interval = 60

        while True:
            rv = self.next_action()
            if rv[0] == 'fetch_list':
                if rv[1]: # Request was successful
                    details = rv[2]
                    if not details['updates'] and not details['deletes']:
                        time.sleep(interval)
                else:
                    time.sleep(interval)
