from bson import json_util
import requests
import time

from documents import ItemsToSyncService


class SyncProcess(object):
    def __init__(self, host, key, secret, database, local_server_key=None, local_server_secret=None):
        self.host = host
        self.key = key
        self.secret = secret
        self.database = database
        self._local_server = None
        self.local_server_key = local_server_key
        self.local_server_secret = local_server_secret
        self.items_to_sync_service = ItemsToSyncService()
        self.should_try_to_resolve_reference = True

    @property
    def local_server(self):
        if self._local_server:
            return self._local_server

        try:
            from MookAPI.services import local_servers
            self._local_server = local_servers.get(
                key=self.local_server_key,
                secret=self.local_server_secret
            )
        except:
            self._local_server = None

        return self._local_server

    def _get_request(self, path):
        url = self.host + path
        # FIXME We ignore SSL errors for now, but verify should be a parameter defaulting to True.
        return requests.get(url, auth=(self.key, self.secret), verify=False)

    def _post_request(self, path, data=None, json=None):
        url = self.host + path
        # FIXME We ignore SSL errors for now, but verify should be a parameter defaulting to True.
        return requests.post(url, data=data, json=json, auth=(self.key, self.secret), verify=False)

    def reset(self):
        r = self._post_request("/local_servers/reset")
        if r.status_code == 200:
            from settings_local import Config
            db_name = Config.MONGODB_DB
            # FIXME Get the MongoDB database name from current_app (requires between in app context)
            db = self.database.connect(db_name)
            db.drop_database(db_name)
            self._local_server = None
            print "Reset successful"
            return True
        else:
            print "Reset failed, status code %d" % r.status_code
            return False, r.status_code

    def fetch_sync_list(self):

        print "Fetching new list of operations"

        r = self._get_request("/local_servers/sync")

        if r.status_code == 200:
            data = json_util.loads(r.text)['data']

            updates = []
            deletes = []

            for item in data['update']:
                db_item = self.items_to_sync_service.create(
                    action='update',
                    url=item['url'],
                    distant_id=item['_id'],
                    class_name=item['_cls'],
                )
                updates.append(db_item)

            for item in data['delete']:
                db_item = self.items_to_sync_service.create(
                    action='delete',
                    distant_id=item['_id'],
                    class_name=item['_cls']
                )
                deletes.append(db_item)

            print "Got response from server."
            if updates or deletes:
                for item in updates:
                    print "* Created task: %s" % item
                for item in deletes:
                    print "* Created task: %s" % item
            else:
                print "==> No new task to create"

            return True, dict(
                updates=updates,
                deletes=deletes
            )

        else:

            print "Could not get response from server, got error %d" % r.status_code

            return False, dict(
                error=r.reason,
                status_code=r.status_code
            )

    def depile_item(self, item):
        print "Performing action: %s" % item
        try:
            result = item.depile(key=self.key, secret=self.secret)
        except:
            return False
        else:
            self.should_try_to_resolve_reference = True
            return result

    def _next_item(self):
        item = self.items_to_sync_service.find(errors__size=0).order_by('queue_position').first()

        if item is None:
            item = self.items_to_sync_service.queryset().order_by('queue_position').first()

        if item is None:
            print "==> No more item to depile"

        return item

    def _post_document(self, document):
        path = "/local_servers/add_item"
        from bson.json_util import dumps, loads
        json = dumps(document.to_json(for_distant=True))
        r = self._post_request(path, json=json)

        if r.status_code == 200:
            response = loads(r.text)
            data = response['data']

            from MookAPI.helpers import get_service_for_class
            service = get_service_for_class(data['_cls'])
            try:
                service.__model__.from_json(
                    data,
                    save=True,
                    from_distant=True,
                    overwrite_document=document
                )
                print "Overwrote local document with information from central server"
            except:
                print "An error occurred while overwriting the local document"
        else:
            print "An error occurred on the central server when trying to send the document"

    def _post_next_document(self):
        print "Checking if there is a document to post to the central server..."
        if self.local_server:
            self.local_server.reload()
            from MookAPI.services import users
            for item in self.local_server.syncable_items:
                if users._isinstance(item.document):
                    for sub_item in item.document.all_syncable_items(local_server=self.local_server):
                        if not sub_item.distant_id:
                            print "Sending document: %s" % sub_item
                            self._post_document(sub_item)
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
        item = self._next_item()

        if item:
            result = self.depile_item(item)
            return 'depile', result

        else:
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
