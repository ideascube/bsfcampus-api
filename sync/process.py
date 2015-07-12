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
            items = json_util.loads(r.text)['items']
            operations = dict(
                new_updates=[],
                new_deletes=[],
                failed_updates=[],
                failed_deletes=[]
            )

            for item in items['update']:
                try:
                    db_item = self.items_to_sync_service.create(
                        action='update',
                        url=item['url'],
                        distant_id=item['_id'],
                        class_name=item['_cls'],
                    )
                except:
                    operations['failed_updates'].append(item)
                else:
                    operations['new_updates'].append(db_item)

            for item in items['delete']:
                try:
                    db_item = self.items_to_sync_service.create(
                        action='delete',
                        distant_id=item['_id'],
                        class_name=item['_cls']
                    )
                except:
                    operations['failed_deletes'].append(item)
                else:
                    operations['new_deletes'].append(db_item)

            return True, operations

        else:
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
            return result

    def _next_item(self):
        item = self.items_to_sync_service.find(errors__size=0).order_by('queue_position').first()

        if item is None:
            item = self.items_to_sync_service.queryset().order_by('queue_position').first()

        return item

    def next_action(self):
        item = self._next_item()
        if item:
            print "Next action: %s" % item
            result = self.depile_item(item)
            return 'depile', result
        else:
            print "No item to depile: fetching new list of operations"
            result, details = self.fetch_sync_list()
            return 'fetch_list', result, details

    def run(self, interval=60):

        while True:
            rv = self.next_action()
            if rv[0] == 'fetch_list' and rv[1]:
                details = rv[2]
                if not details['new_updates'] and not details['new_deletes']:
                    time.sleep(interval)
