from bson import json_util

from MookAPI.core import db, Service


class SyncTask(db.Document):
    """A document that describes a sync operation to perform on the local server."""

    ### PROPERTIES

    queue_position = db.SequenceField()
    """An auto-incrementing counter determining the order of the operations to perform."""

    type = db.StringField(choices=('update', 'delete'))
    """The operation to perform (``update`` or ``delete``)."""

    central_id = db.ObjectIdField()
    """The ``id`` of the ``SyncableDocument`` on the central server."""

    class_name = db.StringField()
    """The class of the ``SyncableDocument`` affected by this operation."""

    url = db.StringField()
    """The URL at which the information of the document can be downloaded. Null if ``type`` is ``delete``."""

    errors = db.ListField(db.StringField())
    """The list of the errors that occurred while trying to perform the operation."""

    def __unicode__(self):
        return "%s %s document with central id %s" % (self.type, self.class_name, self.central_id)

    _service = None
    @property
    def service(self):
        if not self._service:
            from MookAPI.helpers import get_service_for_class
            self._service = get_service_for_class(self.class_name)
        return self._service

    @property
    def model(self):
        return self.service.__model__

    def _fetch_update(self, connector, local_document):
        r = connector.get(self.url)

        if r.status_code == 200:
            son = json_util.loads(r.text)
            document = self.model.from_json(
                son['data'],
                from_central=True,
                overwrite_document=local_document,
                upload_path=connector.local_files_path
            )
            document.clean()
            document.save(validate=False) # FIXME MongoEngine bug, hopefully fixed in next version
            return document

        else:
            raise Exception("Could not fetch info, got status code %d" % r.status_code)

    def _update_local_server(self, connector, local_document):
        tracks_before = set(local_document.synced_tracks)
        users_before = set(local_document.synced_users)

        document = self._fetch_update(connector, local_document)

        if document:
            from . import sync_tasks_service


            tracks_after = set(document.synced_tracks)
            users_after = set(document.synced_users)

            for new_track in tracks_after - tracks_before:
                sync_tasks_service.fetch_tasks_whole_track(new_track.id, connector)
            for new_user in users_after - users_before:
                sync_tasks_service.fetch_tasks_whole_user(new_user.id, connector)
            for obsolete_track in tracks_before - tracks_after:
                sync_tasks_service.create_delete_task_existing_document(obsolete_track)
            for obsolete_user in users_before - users_after:
                sync_tasks_service.create_delete_task_existing_document(obsolete_user)

        return document


    def _depile_update(self, connector):
        try:
            local_document = self.service.get(central_id=self.central_id)
        except Exception as e: # TODO Distinguish between not found and found >1 results
            local_document = None

        if local_document:
            from MookAPI.services import local_servers
            if local_servers._isinstance(local_document):
                return self._update_local_server(connector, local_document)

        return self._fetch_update(connector, local_document)


    def _depile_delete(self):
        try:
            local_document = self.service.get(central_id=self.central_id)
        except Exception as e:
            pass # FIXME What should we do in that case?
        else:
            for document in reversed(local_document.all_synced_documents()):
                document.delete()

        return True


    def depile(self, connector=None):

        rv = False

        try:
            if self.type == 'update':
                rv = self._depile_update(connector=connector)
            elif self.type == 'delete':
                rv = self._depile_delete()
            else:
                self.errors.append("Unrecognized task type")
                self.save()
                return False
        except Exception as e:
            self.errors.append(e.message or e.strerror)
            self.save()
            rv = False
        else:
            self.delete()

        return rv


class SyncTasksService(Service):
    __model__ = SyncTask

    def create_update_task(self, item):
        return self.create(
            type='update',
            url=item['url'],
            central_id=item['_id'],
            class_name=item['_cls'],
        )

    def create_delete_task(self, item):
        return self.create(
            type='delete',
            central_id=item['_ref'].id,
            class_name=item['_cls']
        )

    def create_delete_task_existing_document(self, document):
        return self.create(
            type="delete",
            central_id=document.central_id,
            class_name=document.__class__.__name__
        )

    def get_next_task(self):
        item = self.find(errors__size=0).order_by('queue_position').first()

        if item is None:
            item = self.queryset().order_by('queue_position').first()

        return item

    def _process_tasks_list(self, data):
        updates = []
        deletes = []

        for item in (data.get('updates', [])):
            db_item = self.create_update_task(item)
            updates.append(db_item)
            print "* Created task: %s" % db_item

        for item in (data.get('deletes', [])):
            db_item = self.create_delete_task(item)
            deletes.append(db_item)
            print "* Created task: %s" % db_item

        if not updates and not deletes:
            print "==> No new task to create"

        return dict(updates=updates, deletes=deletes)

    def _process_response(self, r):
        if r.status_code == 200:
            print "Response from server is OK."
            data = json_util.loads(r.text)['data']
            return True, self._process_tasks_list(data)

        else:
            print "Got error code %d from server" % r.status_code
            return False, dict(
                error=r.reason,
                status_code=r.status_code
            )

    def fetch_new_tasks(self, connector):
        print "Fetching new list of operations"
        r = connector.fetch_list()
        return self._process_response(r)

    def fetch_tasks_whole_track(self, track_central_id, connector):
        r = connector.fetch_list_whole_track(track_central_id)
        return self._process_response(r)

    def fetch_tasks_whole_user(self, user_central_id, connector):
        r = connector.fetch_list_whole_user(user_central_id)
        return self._process_response(r)

