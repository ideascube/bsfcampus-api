import time

from documents import SyncTasksService

sync_tasks_service = SyncTasksService()

class SyncProcess(object):

    def __init__(self, connector, local_server, **kwargs):
        self.connector = connector
        self.local_server = local_server
        self.should_try_to_resolve_reference = True

    def fetch_sync_list(self):
        return sync_tasks_service.fetch_new_tasks(connector=self.connector)

    def depile_item(self, item):
        print "Performing action: %s" % item
        try:
            result = item.depile(connector=self.connector)
        except:
            return False
        else:
            self.should_try_to_resolve_reference = True
            return result

    def _post_documents(self, documents):
        from bson.json_util import dumps, loads
        documents_json = [(d.id, d.to_json(for_central=True)) for d in documents]
        r = self.connector.send_documents(json=dumps(documents_json))

        if r.status_code == 200:
            response = loads(r.text)
            central_documents = response['data']

            from MookAPI.helpers import get_service_for_class
            for (local_id, central_document) in central_documents:
                service = get_service_for_class(central_document['_cls'])
                try:
                    for document in documents:
                        if document.id == local_id:
                            overwrite_document = document
                            break

                    if not overwrite_document:
                        break #FIXME Throw exception

                    updated_document = service.__model__.from_json(
                        central_document,
                        from_central=True,
                        overwrite_document=overwrite_document
                    )
                    updated_document.clean()
                    updated_document.save(validate=False) # FIXME MongoEngine bug, hopefully be fixed in next version
                    print "Overwrote local document with information from central server"
                except:
                    print "An error occurred while overwriting the local document"
        else:
            print "An error occurred on the central server when trying to send the document"

    def _post_next_documents(self):
        print "Checking if there is a document to post to the central server..."
        self.local_server.reload()
        from MookAPI.services import users, user_credentials
        for user in self.local_server.synced_users:
            documents_to_post = [
                d for d in user.all_synced_documents(local_server=self.local_server)
                if not d.central_id #FIXME This doesn't detect changes in local documents (users or credentials)
            ]
            for document in documents_to_post:
                if users._isinstance(document) or user_credentials._isinstance(document):
                    self._post_documents([document])
                    return True
            if documents_to_post:
                self._post_documents(documents_to_post)
                return True
        print "No more document to post"
        return False

    def post_all_documents(self):
        succeeded = True
        counter = 0
        while succeeded:
            succeeded = self._post_next_documents()
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
