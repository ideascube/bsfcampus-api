import datetime
import os

from mongoengine.common import _import_class
import requests

from MookAPI import db


class MongoCoderMixin(object):
    """
    .. _MongoCoderMixin:

    A mixin that provides methods to encode and decode JSON representations of MongoEngine ``Document`` and ``EmbeddedDocument`` objects.
    This mixin is called in MongoCoderDocument_ and MongoCoderEmbeddedDocument_.
    """

    def encode_mongo(self, instance=None):
        """
        .. _encode_mongo:

        Alternative to native MongoEngine method ``to_mongo``
        Generates a JSON representation of the document.
        When they are available, any ``FileField`` named ``key`` will be represented with three keys in the JSON representation:

        * ``key`` is the ObjectId of the file;
        * ``key_url`` is the URL at which the file can be downloaded (requires accordingly-named virtual property to be implemented in subclass);
        * ``key_filename`` is the name of the file.

        Embedded documents (and lists thereof) that inherit from MongoCoderEmbeddedDocument_ will recursively be serialized using ``encode_mongo``
        """

        if instance is None and isinstance(self, db.Document):
            instance = self

        son = self.to_mongo()

        FileField = _import_class('FileField')
        EmbeddedDocumentField = _import_class('EmbeddedDocumentField')
        ListField = _import_class('ListField')

        for key in son.iterkeys():
            key = self._reverse_db_field_map.get(key, key)
            if key in self._fields:
                field = self._fields.get(key)

                ## Add URL and filename of any FileField.
                if isinstance(field, FileField):
                    value = getattr(self, key, None)
                    if not value:
                        continue
                    url_key = key + '_url'
                    filename_key = key + '_filename'
                    try:
                        son[url_key] = getattr(self, url_key)
                    except:
                        pass
                    son[filename_key] = value.filename

                ## Recursively encode embedded documents....
                elif isinstance(field, EmbeddedDocumentField):
                    if issubclass(field.document_type_obj, MongoCoderEmbeddedDocument):
                        embedded_doc = getattr(self, key)
                        if instance is not None:
                            embedded_doc._instance = instance
                        son[key] = embedded_doc.encode_mongo(instance)

                ## ...or lists thereof.
                elif isinstance(field, ListField):
                    if isinstance(field.field, EmbeddedDocumentField):
                        if issubclass(field.field.document_type_obj, MongoCoderEmbeddedDocument):
                            array = getattr(self, key)
                            encoded_array = []
                            for element in array:
                                if instance is not None:
                                    element._instance = instance
                                encoded_element = element.encode_mongo(instance)
                                encoded_array.append(encoded_element)
                            son[key] = encoded_array

        return son

    @staticmethod
    def _convert_value_from_json(value, field):

        ReferenceField = _import_class('ReferenceField')
        EmbeddedDocumentField = _import_class('EmbeddedDocumentField')
        ListField = _import_class('ListField')

        ## ReferenceField: convert reference to use the local ``id`` instead of the distant one.
        if isinstance(field, ReferenceField):
            value = field.to_python(value)
            return field.document_type_obj.objects(distant_id=value.id).first()

        ## EmbeddedDocumentField: instantiate MongoCoderEmbeddedDocument from JSON
        elif isinstance(field, EmbeddedDocumentField):
            return field.document_type_obj._decode_mongo(value)

        ## ListField: recursively convert all elements in the list
        elif isinstance(field, ListField):
            ## field.field is the type of elements in the listfield
            if field.field is None:
                return field.to_python(value)

            converted_value = []
            for element in value:
                converted_element = MongoCoderMixin._convert_value_from_json(element, field.field)
                converted_value.append(converted_element)

            return converted_value

        else:
            return field.to_python(value)

    def _set_value_from_json(self, json, key):

        ## Get value from json
        value = json[key]
        if value is None:
            return

        ## Check if key is valid and has an associated Field object
        key = self._reverse_db_field_map.get(key, key)
        if key in self._fields or key in ('id', 'pk', '_cls'):
            field = self._fields.get(key)
            if not field:
                return
        else:
            return

        ## Special case: FileField requires special method to set value
        FileField = _import_class('FileField')
        if isinstance(field, FileField):
            url_key = key + '_url'
            filename_key = key + '_filename'
            url = json[url_key]
            filename = json[filename_key] or 'temp'
            with open(filename, 'wb') as handle:
                r = requests.get(url, stream=True)
                if not r.ok:
                    return  # Raise an exception
                for block in r.iter_content(1024):
                    if not block:
                        break
                    handle.write(block)
            value = open(filename, 'rb')

            self[key].put(value, content_type=r.headers['content-type'], filename=filename)
            os.remove(filename)
        ## Any other type: convert value before setting using setattr
        else:
            value = self._convert_value_from_json(value, field)
            setattr(self, key, value)


class MongoCoderDocument(db.Document, MongoCoderMixin):
    """
    .. _MongoCoderDocument:

    A MongoEngine ``Document`` with the MongoCoderMixin_ in order to encode and decode JSON representations.
    """

    meta = {
    'allow_inheritance': True,
    'abstract': True
    }

    @property
    def url(self):
        """
        The URL where a JSON representation of the document based on MongoCoderMixin_'s encode_mongo_ method can be found.

        .. warning::

            Subclasses of MongoCoderDocument should implement this method.
        """

        raise exceptions.NotImplementedError("The single-object URL of this document class is not defined.")

    @classmethod
    def json_key(cls):
        """
        When a view returns the JSON representation of a ``MongoCoderDocument``, the JSON object is wrapped in a single-key dictionary, as per REST conventions.
        This class method returns the name of this key.
        Defaults to the lowercase name of the class.
        """
        return cls.__name__.lower()

    @classmethod
    def json_key_collection(cls):
        """
        When a view returns the JSON representation of a list of ``MongoCoderDocument`` objects, the JSON object is wrapped in a single-key dictionary, as per REST conventions.
        This class method returns the name of this key.
        Defaults to the lowercase name of the class with a appended 's'.
        """
        return cls.json_key() + 's'

    def reference(self):
        """
        Returns a JSON object to reference the current document. The JSON document may contain three keys:

        * ``_cls``: the name of the ``Document`` class;
        * ``_ref``: a DBRef to the document;
        * ``url``: the URL given by the ``url`` virtual property, if implemented.
        """
        son = {}
        son['_cls'] = type(self).__name__
        son['_ref'] = self.to_dbref()
        try:
            son['url'] = self.url
        except:
            pass
        return son

    @classmethod
    def decode_mongo(cls, json):
        """
        Returns a ``MongoCoderDocument`` instance using an unwrapped JSON representation.
        """

        obj = cls()

        for key in json.iterkeys():
            obj._set_value_from_json(json, key)

        return obj

    @classmethod
    def decode_json_result(cls, json):
        """
        Returns a ``MongoCoderDocument`` instance using a JSON representation wrapped in a single-key dictionary as per REST conventions.
        """

        return cls.decode_mongo(json[cls.json_key()])


class MongoCoderEmbeddedDocument(db.EmbeddedDocument, MongoCoderMixin):
    """
    .. _MongoCoderEmbeddedDocument:

    A MongoEngine ``EmbeddedDocument`` with the MongoCoderMixin_ in order to encode and decode JSON representations.
    """

    meta = {
    'allow_inheritance': True,
    'abstract': True
    }

    @classmethod
    def _decode_mongo(cls, json):
        obj = cls()

        for key in json.iterkeys():
            obj._set_value_from_json(json, key)

        return obj


class DeletedSyncableDocument(MongoCoderDocument):
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


## All documents that need to be synced must inherit from this class.
class SyncableDocument(MongoCoderDocument):
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

    def all_syncable_items(self):
        """
        Returns the list of references to atomic documents that should be looked at when syncing this document.
        Defaults to a one-element list containing a reference to self.

        .. note::

            Override this method if this document has children documents.
        """

        return [self.reference()]

    def items_to_update(self, last_sync):
        """
        .. _items_to_update:

        Returns the list of references to atomic documents that have changed since the last synchronization.
        Defaults to a one-element list containing a reference to self.

        .. note::

            Override this method if this document has children documents.
        """

        if last_sync is None or self.last_modification is None or last_sync < self.last_modification:
            return [self.reference()]

        return []

    def items_to_delete(self, last_sync):
        """
        .. _items_to_delete:

        Returns the list of references to atomic documents that have been deleted since the last synchronization.
        This method will also automatically check for any deleted children documents (no need to override as long as ``top_level_document`` is overridden).
        """

        items = []

        for obj in DeletedSyncableDocument.objects.filter(top_level_document=self.top_level_syncable_document()):
            if last_sync is None or obj.date is None or last_sync < obj.date:
                document = obj.encode_mongo()['document']
                items.append(document)

        return items

    def items_to_sync(self, last_sync):
        """
        Returns a dictionary ``dict`` with two keys:

        * ``dict['update']`` contains the results of the items_to_update_ method;
        * ``dict['delete']`` contains the results of the items_to_delete_ method.

        .. todo::

            Remove items that are in the ``delete`` list from the ``update`` list.
        """

        items = {}
        items['update'] = self.items_to_update(last_sync)
        items['delete'] = self.items_to_delete(last_sync)
        ## We should do some cleanup at this point, in particular remove deletable items from 'update' list.
        return items

    @classmethod
    def decode_mongo(cls, mongo):
        obj = super(SyncableDocument, cls).decode_mongo(mongo)

        obj.distant_id = mongo['_id']

        return obj
