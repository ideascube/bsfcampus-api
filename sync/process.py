from bson import json_util
import requests
import time

from documents import ItemsToSyncService


class SyncProcess(object):
    def __init__(self, host, key, secret):
        self.host = host
        self.key = key
        self.secret = secret
        self.items_to_sync_service = ItemsToSyncService()
        self.should_try_to_resolve_reference = False

    def _get_request(self, path):
        url = self.host + path
        return requests.get(url, auth=(self.key, self.secret))

    def reset(self):
        r = self._get_request("/local_servers/reset")
        if r.status_code == 200:
            print "Reset successful"
            return True
        else:
            print "Reset failed, status code %d" % r.status_code
            return False, r.status_code

    def fetch_sync_list(self):
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

        return item

    def resolve_references(self):
        if self.should_try_to_resolve_reference:
            from MookAPI.sync import UnresolvedReference
            for unresolved_ref in UnresolvedReference.objects.all():
                unresolved_ref.resolve()
            self.should_try_to_resolve_reference = False

    def next_action(self):
        item = self._next_item()
        if item:
            print "Next action: %s" % item
            result = self.depile_item(item)
            return 'depile', result
        else:
            print "No item to depile"
            self.resolve_references()
            print "Fetching new list of operations"
            result, details = self.fetch_sync_list()
            return 'fetch_list', result, details

    def run(self, interval=60):

        while True:
            rv = self.next_action()
            if rv[0] == 'fetch_list':
                if rv[1]: # Request was successful
                    details = rv[2]
                    if not details['updates'] and not details['deletes']:
                        time.sleep(interval)
                else:
                    time.sleep(interval)
