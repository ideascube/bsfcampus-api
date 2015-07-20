import csv, codecs, cStringIO
import os
import requests
from bson import json_util
from mongoengine.common import _import_class

from flask.json import JSONEncoder as BaseJSONEncoder

from .core import db

class JsonSerializer(object):

    __json_public__ = None
    __json_hidden__ = None
    __json_additional__ = None
    __json_modifiers__ = None
    __json_rename__ = None
    __json_dbref__ = None

    def encode_mongo(self, fields=None, for_distant=False):

        Document = _import_class('Document')
        EmbeddedDocument = _import_class('EmbeddedDocument')

        if not isinstance(self, (Document, EmbeddedDocument)):
            raise TypeError("This object is not a MongoEngine (embedded) document.")

        FileField = _import_class('FileField')
        EmbeddedDocumentField = _import_class('EmbeddedDocumentField')
        ListField = _import_class('ListField')
        ReferenceField = _import_class('ReferenceField')
        GenericReferenceField = _import_class('GenericReferenceField')

        rv = self.to_mongo(fields=fields)

        for key in rv.iterkeys():
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
                        rv[url_key] = getattr(self, url_key)
                        rv[filename_key] = value.filename
                    except:
                        pass

                elif isinstance(field, (ReferenceField, GenericReferenceField)):
                    value = getattr(self, key, None)
                    if value:
                        rv[key] = value.to_json_dbref(for_distant=for_distant)

                ## Recursively encode embedded documents....
                elif isinstance(field, EmbeddedDocumentField):
                    if issubclass(field.document_type_obj, JsonSerializer):
                        value = getattr(self, key, None)
                        if value:
                            rv[key] = value.to_json(for_distant=for_distant)

                ## ...or lists thereof.
                elif isinstance(field, ListField):
                    if isinstance(field.field, EmbeddedDocumentField):
                        if issubclass(field.field.document_type_obj, JsonSerializer):
                            values = getattr(self, key, [])
                            rv[key] = [value.to_json(for_distant=for_distant) for value in values]
                    elif isinstance(field.field, (ReferenceField, GenericReferenceField)):
                        values = getattr(self, key, [])
                        rv[key] = [value.to_json_dbref(for_distant=for_distant) for value in values]

        return rv

    def get_field_names(self):
        Document = _import_class('Document')
        EmbeddedDocument = _import_class('EmbeddedDocument')
        if isinstance(self, (Document, EmbeddedDocument)):
            return self._fields.keys()
        elif self.__dict__:
            return self.__dict__.keys()
        return []

    def to_json(self, for_distant=False):
        field_names = self.get_field_names()

        public = self.__json_public__ or field_names
        hidden = self.__json_hidden__ or []
        additional = self.__json_additional__ or []
        modifiers = self.__json_modifiers__ or dict()
        renames = self.__json_rename__ or dict()

        Document = _import_class('Document')
        EmbeddedDocument = _import_class('EmbeddedDocument')
        if isinstance(self, (Document, EmbeddedDocument)):
            rv = self.encode_mongo(fields=public, for_distant=for_distant)
        else:
            rv = dict()
            for key in public:
                rv[key] = getattr(self, key)

        for key in additional:
            rv[key] = getattr(self, key)
        for key, modifier in modifiers.items():
            rv[key] = modifier(rv[key], self)
        for key in hidden:
            rv.pop(key, None)
        for key_before, key_after in renames.items():
            try:
                rv[key_after] = rv[key_before]
                rv.pop(key_before, None)
            except:
                pass

        if for_distant:
            rv['_id'] = rv.pop('distant_id', None)

        return rv

    def to_json_dbref(self, for_distant=False):
        fields = self.__json_dbref__ or []
        renames = self.__json_rename__ or dict()

        rv = dict()
        if for_distant and hasattr(self, 'distant_id'):
            rv['_id'] = self.distant_id
        else:
            rv['_id'] = self.id
        rv['_cls'] = self.__class__.__name__
        for key in fields:
            rv[key] = getattr(self, key)
        for key_before, key_after in renames.items():
            try:
                rv[key_after] = rv[key_before]
                rv.pop(key_before, None)
            except KeyError:
                pass

        return rv

    @staticmethod
    def _convert_value_from_json(value, field, instance, from_distant, path_in_instance, unresolved_references):

        if field is None:
            return field.to_python(value)

        ReferenceField = _import_class('ReferenceField')
        GenericReferenceField = _import_class('GenericReferenceField')
        EmbeddedDocumentField = _import_class('EmbeddedDocumentField')
        ListField = _import_class('ListField')

        ## ReferenceField: convert reference to use the local ``id`` instead of the distant one.
        if isinstance(field, ReferenceField):
            # FIXME This way of getting the id is not really clean.
            value = field.to_python(value['_id'])
            document_id = value.id
            if from_distant:
                try:
                    document = field.document_type_obj.objects.get(distant_id=document_id)
                    return document
                except Exception as e:
                    from MookAPI.sync import UnresolvedReference
                    ref = UnresolvedReference()
                    ref.field_path = field.name
                    ref.class_name=field.document_type_obj.__name__
                    ref.distant_id=document_id
                    unresolved_references.append(ref)
                    return None
            else:
                try:
                    document = field.document_type_obj.objects.get(id=document_id)
                    return document
                except Exception as e:
                    return None

        ## GenericField: convert reference to use the local ``id`` instead of the distant one.
        elif isinstance(field, GenericReferenceField):
            # FIXME This way of getting the id is not really clean.
            try:
                service = _get_service_for_class(value['_cls'])
                document = service.get(distant_id=value['_id'])
                return document
            except:
                from MookAPI.sync import UnresolvedReference
                ref = UnresolvedReference()
                ref.field_path = field.name
                ref.class_name=field.document_type_obj.__name__
                ref.distant_id=value['_id']
                unresolved_references.append(ref)
                return None

        ## EmbeddedDocumentField: instantiate MongoCoderEmbeddedDocument from JSON
        elif isinstance(field, EmbeddedDocumentField):
            next_path_in_instance = ("%s.%s" % (path_in_instance, field.name)).lstrip('.')
            return field.document_type_obj.from_json(
                value,
                path_in_instance=next_path_in_instance,
                instance=instance,
                unresolved_references=unresolved_references
            )

        ## ListField: recursively convert all elements in the list
        elif isinstance(field, ListField):
            ## field.field is the type of elements in the listfield
            converted_value = []
            missing_refs = []
            for index, element in enumerate(value):
                next_path_in_instance = ("%s.%s[%d]" % (path_in_instance, field.name, index)).lstrip('.')
                value = JsonSerializer._convert_value_from_json(
                    value=element,
                    field=field.field,
                    instance=instance,
                    from_distant=from_distant,
                    path_in_instance=next_path_in_instance,
                    unresolved_references=unresolved_references
                )
                converted_value.append(value)

            return converted_value

        else:
            return field.to_python(value)

    def _set_value_from_json(self, json, key, instance, **kwargs):

        from_distant = kwargs.get('from_distant', False)
        path_in_instance = kwargs.get('path_in_instance', '')
        unresolved_references = kwargs.get('unresolved_references', [])

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

        FileField = _import_class('FileField')

        if isinstance(field, FileField):
            url_key = key + '_url'
            filename_key = key + '_filename'
            url = json[url_key]
            # FIXME: add a dir path for these temp files
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
            # FIXME: fix Windows specific error when deleting file
            try:
                os.remove(filename)
            except:
                pass

        else:
            value = self._convert_value_from_json(
                value=value,
                field=field,
                instance=instance,
                from_distant=from_distant,
                path_in_instance=path_in_instance,
                unresolved_references=unresolved_references
            )
            setattr(self, key, value)

    @classmethod
    def from_json(cls, json, **kwargs):

        save = kwargs.get('save', False)
        from_distant = kwargs.get('from_distant', False)
        overwrite_document = kwargs.get('overwrite_document', None)
        instance = kwargs.get('instance', None)
        path_in_instance = kwargs.get('path_in_instance', '')
        unresolved_references = kwargs.get('unresolved_references', [])

        obj = cls()

        if not instance:
            instance = obj

        for key in json.iterkeys():
            obj._set_value_from_json(
                json,
                key,
                from_distant=from_distant,
                instance=instance,
                path_in_instance=path_in_instance,
                unresolved_references=unresolved_references
            )

        if from_distant:
            obj.distant_id = obj.id
            obj.id = None

        if overwrite_document:
            obj.id = overwrite_document.id

        if save:
            Document = _import_class('Document')
            if isinstance(obj, Document):
                obj.save()
                for ref in unresolved_references:
                    ref.document = instance
                    ref.save()

        return obj

    def set_value_for_field_path(self, value, field_path):
        setattr(self, field_path, value) # FIXME handle field path recursively


class JSONEncoder(BaseJSONEncoder):
    def default(self, o):
        if isinstance(o, db.QuerySet):
            return map(lambda d: d.to_json(), o)
        if isinstance(o, JsonSerializer):
            return o.to_json()
        try:
            return json_util.default(o)
        except:
            return super(JSONEncoder, self).default(o)


class CsvSerializer(object):
    def to_csv(self):
        is_list = False
        if self.to_csv_rows():
            is_list = True
            rv = self.to_csv_rows()
        elif self.to_csv_row():
            rv = self.to_csv_row()
        else:
            field_names = self.get_field_names_for_csv() or self.get_field_names()
            rv = self.to_csv_from_field_names(field_names)

        return rv, is_list

    def to_csv_from_field_names(self, field_names):
        rv = []
        Document = _import_class('Document')
        ObjectIdField = _import_class('ObjectIdField')
        DateTimeField = _import_class('DateTimeField')
        for key in field_names:
            field = getattr(self, key)
            csv_value = ""
            if field is not None:
                if isinstance(field, Document):
                    csv_value = unicode(field.id)
                elif isinstance(field, DateTimeField):
                    csv_value = field.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    csv_value = unicode(field)
            rv.append(csv_value)
        return rv

    def get_field_names(self):
        Document = _import_class('Document')
        EmbeddedDocument = _import_class('EmbeddedDocument')
        if isinstance(self, (Document, EmbeddedDocument)):
            return self._fields.keys()
        elif self.__dict__:
            return self.__dict__.keys()
        return []

    def to_csv_row(self):
        """ this method returns None as it should be overridden if necessary """
        return None

    def to_csv_rows(self):
        """ this method returns None as it should be overridden if necessary """
        return None

    def get_field_names_for_csv(self):
        """ this method returns None as it should be overridden if necessary """
        return None


class UnicodeCSVWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writeactivity(self, o):
        if isinstance(o, CsvSerializer):
            csv_data, is_list = o.to_csv()
            if is_list:
                self.writerows(csv_data)
            else:
                self.writerow(csv_data)

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
