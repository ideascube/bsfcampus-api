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

    def _get_service(self):
        from MookAPI.helpers import get_service_for_class
        return get_service_for_class(self.class_name)

    def _depile_update(self, connector):
        service = self._get_service()

        try:
            local_document = service.get(central_id=self.central_id)
        except Exception as e: # TODO Distinguish between not found and found >1 results
            local_document = None

        r = connector.get(self.url)

        if r.status_code == 200:
            son = json_util.loads(r.text)
            document = service.__model__.from_json(
                son['data'],
                from_central=True,
                overwrite_document=local_document
            )
            document.clean()
            document.save(validate=False) # FIXME MongoEngine bug, hopefully be fixed in next version
            return document

        else:
            raise Exception("Could not fetch info, got status code %d" % r.status_code)

    def _depile_delete(self):
        service = self._get_service()
        local_documents = service.find(central_id=self.central_id)
        for document in local_documents:
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

    def get_next_task(self):
        item = self.find(errors__size=0).order_by('queue_position').first()

        if item is None:
            item = self.queryset().order_by('queue_position').first()

        return item
