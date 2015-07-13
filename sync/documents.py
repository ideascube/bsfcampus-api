from bson import json_util

from MookAPI.core import db, Service


class ItemToSync(db.Document):
    """A document that describes a sync operation to perform on the local server."""

    ### PROPERTIES

    queue_position = db.SequenceField()
    """An auto-incrementing counter determining the order of the operations to perform."""

    distant_id = db.ObjectIdField()
    """The ``id`` of the ``SyncableDocument`` on the central server."""

    class_name = db.StringField()
    """The class of the ``SyncableDocument`` affected by this operation."""

    action = db.StringField(choices=('update', 'delete'))
    """The operation to perform (``update`` or ``delete``)."""

    url = db.StringField()
    """The URL at which the information of the document can be downloaded. Null if ``action`` is ``delete``."""

    errors = db.ListField(db.StringField())
    """The list of the errors that occurred while trying to perform the operation."""

    def __unicode__(self):
        return "%s %s document with distant id %s" % (self.action, self.class_name, self.distant_id)

    def raw_class_name(self):
        return self.class_name.split('.')[-1]

    def _get_service(self):
        import MookAPI.services as s
        class_name = self.raw_class_name()
        for name, service in s.__dict__.iteritems():
            if isinstance(service, Service):
                if service.__model__.__name__ == class_name:
                    return service
        raise KeyError("Class name unrecognized")

    def _depile_update(self, key, secret):
        service = self._get_service()
        local_documents = service.find(distant_id=self.distant_id)

        if local_documents.count() > 1:
            raise Exception("Unexpectedly found two local documents with given distant id")

        local_document = local_documents.first()

        import requests
        r = requests.get(self.url, auth=(key, secret))

        if r.status_code == 200:
            son = json_util.loads(r.text)
            document = service.__model__.from_json(son['data'], distant=True)
            if local_document:
                document.id = local_document.id
            return document.save()

        else:
            raise Exception("Could not fetch info, got status code %d" % r.status_code)

    def _depile_delete(self):
        service = self._get_service()
        local_documents = service.find(distant_id=self.distant_id)
        for document in local_documents:
            document.delete()

        return True

    def depile(self, key=None, secret=None):

        rv = False

        try:
            if self.action == 'update':
                rv = self._depile_update(key=key, secret=secret)
            elif self.action == 'delete':
                rv = self._depile_delete()
            else:
                self.errors.append("Unrecognized action")
                self.save()
                return False
        except Exception as e:
            self.errors.append(e.message)
            self.save()
            rv = False
        else:
            self.delete()

        return rv


class ItemsToSyncService(Service):
    __model__ = ItemToSync
