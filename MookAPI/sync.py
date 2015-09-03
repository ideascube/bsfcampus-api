import datetime
import exceptions
import collections

from MookAPI.core import db
from MookAPI.serialization import JsonSerializer


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

    central_id = db.ObjectIdField()

    def resolve(self):
        print "Trying to resolve %s" % unicode(self)
        try:
            from MookAPI.helpers import get_service_for_class
            service = get_service_for_class(self.class_name)
            local_document = service.get(central_id=self.central_id)
            self.document.set_value_for_field_path(local_document, self.field_path)
            self.document.clean()
            self.document.save(validate=False) # FIXME MongoEngine bug
            self.delete()
            print "==> Success!"
            return True
        except Exception as e:
            print "==> Failed!"
            return False

    def __unicode__(self):
        try:
            return "Reference to %s document %s in document %s at field path %s" \
                   % (self.class_name, str(self.central_id), self.document, self.field_path)
        except:
            return "Reference to %s document %s in %s document at field path %s" \
                   % (self.class_name, str(self.central_id), self.document.__class__.__name__, self.field_path)


class SyncableDocumentJsonSerializer(JsonSerializer):
    __json_hierarchy_skeleton__ = None

    def to_json_dbref(self, for_central=False):
        son = super(SyncableDocumentJsonSerializer, self).to_json_dbref(for_central=for_central)
        try:
            # FIXME Check if server is central instead (which means we need to be in application context)
            son['url'] = self.url
        except:
            pass
        return son

    def to_json_search_result(self):
        son = self.to_json_dbref()
        try:
            son['description'] = self.description
            son['hierarchy'] = self.hierarchy
        except:
            pass
        return son

    def to_json_hierarchy_skeleton(self):
        fields = self.__json_hierarchy_skeleton__ or []
        renames = self.__json_rename__ or dict()

        rv = self.to_json_dbref()
        for key in fields:
            value = getattr(self, key)
            if isinstance(value, collections.Iterable):
                rv[key] = []
                for child in value:
                    if isinstance(child, SyncableDocumentJsonSerializer):
                        rv[key].append(child.to_json_hierarchy_skeleton())
                    else:
                        rv[key].append(child)
            elif isinstance(value, SyncableDocumentJsonSerializer):
                rv[key] = value.to_json_hierarchy_skeleton()
            else:
                rv[key] = value
        for key_before, key_after in renames.items():
            try:
                rv[key_after] = rv[key_before]
                rv.pop(key_before, None)
            except KeyError:
                pass

        return rv


class SyncableDocument(SyncableDocumentJsonSerializer, db.Document):
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
    central_id = db.ObjectIdField()
    """The id of the document on the central server."""

    # A placeholder for unresolved references that need to be saved after the document is saved
    unresolved_references = []

    @property
    def url(self, _external=False):
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

        rv = super(SyncableDocument, self).save(*args, **kwargs)

        for ref in self.unresolved_references:
            ref.document = self
            ref.save()

        return rv

    def delete(self, *args, **kwargs):
        reference = DeletedSyncableDocument()
        reference.document = self.to_json_dbref()
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

    def items_to_update(self, local_server):
        """
        .. _items_to_update:

        Returns the list of references to atomic documents that have changed since the last synchronization.
        Defaults to a one-element list containing a reference to self.

        .. note::

            Override this method if this document has children documents.
        """

        items = []
        last_sync = local_server.last_sync

        for item in self.all_syncable_items(local_server=local_server):
            if last_sync is None or item.last_modification is None or last_sync < item.last_modification:
                items.append(item)

        return items

    def items_to_delete(self, local_server):
        """
        .. _items_to_delete:

        Returns the list of references to atomic documents that have been deleted since the last synchronization.
        This method will also automatically check for any deleted children documents (no need to override as long as ``top_level_document`` is overridden).
        """

        items = []
        last_sync = local_server.last_sync

        for obj in DeletedSyncableDocument.objects.no_dereference().filter(top_level_document=self.top_level_syncable_document()):
            if last_sync is None or obj.date is None or last_sync < obj.date:
                items.append(obj.document)

        return items

    def items_to_sync(self, local_server=None):
        """
        Returns a dictionary ``dict`` with two keys:

        * ``dict['update']`` contains the results of the items_to_update_ method;
        * ``dict['delete']`` contains the results of the items_to_delete_ method.

        .. todo::

            Remove items that are in the ``delete`` list from the ``update`` list.
        """

        items = {}
        items['update'] = self.items_to_update(local_server=local_server)
        items['delete'] = self.items_to_delete(local_server=local_server)
        ## We should do some cleanup at this point, in particular remove deletable items from 'update' list.
        return items

    def __unicode__(self):
        return "Document with class %s and id %s" % (self.__class__.__name__, str(self.id))
