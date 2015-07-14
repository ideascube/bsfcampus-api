import datetime
import exceptions

from MookAPI.core import db
from MookAPI.helpers import JsonSerializer


class DeletedSyncableDocument(JsonSerializer, db.Document):
    """
    .. _DeletedSyncableDocument:

    A collection that references all SyncableDocument_ objects that have been deleted, so that they can be deleted on local servers at the next synchronization.
    The ``delete`` method of SyncableDocument_ creates a ``DeletedSyncableDocument`` object.
    """

    document = db.GenericReferenceField()
    """A DBRef to the document that was deleted."""

    top_level_document = db.GenericReferenceField()
    """A DBRef to the top-level document of the deleted document, if this is a child document."""

    date = db.DateTimeField()
    """The date at which the document was deleted."""

    def save(self, *args, **kwargs):
        self.top_level_document = self.document.top_level_syncable_document()
        if self.date is None:
            self.date = datetime.datetime.now()
        return super(DeletedSyncableDocument, self).save(*args, **kwargs)


class UnresolvedReference(JsonSerializer, db.Document):

    document = db.GenericReferenceField()

    field_path = db.StringField()

    class_name = db.StringField()

    distant_id = db.ObjectIdField()

    def resolve(self):
        print "Trying to resolve %s" % self
        try:
            from MookAPI.helpers import _get_service_for_class
            service = _get_service_for_class(self.class_name)
            local_document = service.get(distant_id=self.distant_id)
            self.document.set_value_for_field_path(local_document, self.field_path)
            self.document.save()
            self.delete()
            print "==> Success!"
            return True
        except:
            print "==> Failed!"
            return False


class SyncableDocument(JsonSerializer, db.Document):
    """
    .. _SyncableDocument:

    An abstract class for any document that needs to be synced between the central server and a local server.
    """

    meta = {
        'allow_inheritance': True,
        'abstract': True
    }

    ## Last modification
    last_modification = db.DateTimeField()
    """
    The date of the last modification on the document.
    Used to determine whether the document has changed since the last synchronization of a local server.
    """

    ## Id of the document on the central server
    distant_id = db.ObjectIdField()
    """The id of the document on the central server."""

    @property
    def url(self):
        """
        The URL where a JSON representation of the document based on MongoCoderMixin_'s encode_mongo_ method can be found.

        .. warning::

            Subclasses of MongoCoderDocument should implement this method.
        """

        raise exceptions.NotImplementedError("The single-object URL of this document class is not defined.")

    def top_level_syncable_document(self):
        """
        If a ``SyncableDocument`` has child documents, this function returns the top-level parent document.
        Defaults to ``self``.

        .. note::

            Override this method if the document is a child of a ``SyncableDocument``.
        """

        return self

    def save(self, *args, **kwargs):
        self.last_modification = datetime.datetime.now()
        return super(SyncableDocument, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        reference = DeletedSyncableDocument()
        reference.document = self
        reference.save()
        return super(SyncableDocument, self).delete(*args, **kwargs)

    def all_syncable_items(self, local_server=None):
        """
        Returns the list of references to atomic documents that should be looked at when syncing this document.
        Defaults to a one-element list containing a reference to self.

        .. note::

            Override this method if this document has children documents.
        """

        return [self]

    def items_to_update(self, last_sync, local_server=None):
        """
        .. _items_to_update:

        Returns the list of references to atomic documents that have changed since the last synchronization.
        Defaults to a one-element list containing a reference to self.

        .. note::

            Override this method if this document has children documents.
        """

        items = []

        for item in self.all_syncable_items(local_server=local_server):
            if last_sync is None or item.last_modification is None or last_sync < item.last_modification:
                items.append(item)

        return items

    def items_to_delete(self, last_sync, local_server=None):
        """
        .. _items_to_delete:

        Returns the list of references to atomic documents that have been deleted since the last synchronization.
        This method will also automatically check for any deleted children documents (no need to override as long as ``top_level_document`` is overridden).
        """

        items = []

        for obj in DeletedSyncableDocument.objects.filter(top_level_document=self.top_level_syncable_document()):
            if last_sync is None or obj.date is None or last_sync < obj.date:
                document = obj.to_json()['document']
                items.append(document)

        return items

    def items_to_sync(self, last_sync, local_server=None):
        """
        Returns a dictionary ``dict`` with two keys:

        * ``dict['update']`` contains the results of the items_to_update_ method;
        * ``dict['delete']`` contains the results of the items_to_delete_ method.

        .. todo::

            Remove items that are in the ``delete`` list from the ``update`` list.
        """

        items = {}
        items['update'] = self.items_to_update(last_sync, local_server=local_server)
        items['delete'] = self.items_to_delete(last_sync, local_server=local_server)
        ## We should do some cleanup at this point, in particular remove deletable items from 'update' list.
        return items

    def to_json_dbref(self):
        son = super(SyncableDocument, self).to_json_dbref()
        son['url'] = self.url
        return son
