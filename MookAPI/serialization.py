import csv, codecs, cStringIO
import collections
import os
import requests
from bson import json_util, DBRef
from mongoengine.common import _import_class

from flask import current_app
from flask.json import JSONEncoder as BaseJSONEncoder

from .core import db

class JsonSerializer(object):

    __json_public__ = None
    __json_hidden__ = None
    __json_additional__ = None
    __json_files__ = None
    __json_modifiers__ = None
    __json_rename__ = None
    __json_dbref__ = None

    @staticmethod
    def make_file_url(path_or_url):
        if path_or_url is None:
            return None
        
        if "://" in path_or_url or path_or_url.startswith("//"):
            return path_or_url
        else:
            return current_app.config.get('UPLOAD_FILES_URL') + path_or_url

    def encode_mongo(self, fields=None, for_central=False):

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
                        if isinstance(value, Document):
                            rv[key] = value.to_json_dbref(for_central=for_central)
                        elif isinstance(value, DBRef):
                            rv[key] = value

                ## Recursively encode embedded documents....
                elif isinstance(field, EmbeddedDocumentField):
                    if issubclass(field.document_type_obj, JsonSerializer):
                        value = getattr(self, key, None)
                        if value:
                            rv[key] = value.to_json(for_central=for_central)

                ## ...or lists thereof.
                elif isinstance(field, ListField):
                    if isinstance(field.field, EmbeddedDocumentField):
                        if issubclass(field.field.document_type_obj, JsonSerializer):
                            values = getattr(self, key, [])
                            rv[key] = [value.to_json(for_central=for_central) for value in values]
                    elif isinstance(field.field, (ReferenceField, GenericReferenceField)):
                        values = getattr(self, key, [])
                        rv[key] = [value.to_json_dbref(for_central=for_central) for value in values]

        return rv

    def get_field_names(self):
        Document = _import_class('Document')
        EmbeddedDocument = _import_class('EmbeddedDocument')
        if isinstance(self, (Document, EmbeddedDocument)):
            return self._fields.keys()
        elif self.__dict__:
            return self.__dict__.keys()
        return []

    def to_json(self, for_central=False):
        field_names = self.get_field_names()

        public = self.__json_public__ or field_names
        hidden = self.__json_hidden__ or []
        additional = self.__json_additional__ or []
        files = self.__json_files__ or []
        modifiers = self.__json_modifiers__ or dict()
        renames = self.__json_rename__ or dict()

        Document = _import_class('Document')
        EmbeddedDocument = _import_class('EmbeddedDocument')
        if isinstance(self, (Document, EmbeddedDocument)):
            rv = self.encode_mongo(fields=public, for_central=for_central)
        else:
            rv = dict()
            for key in public:
                rv[key] = getattr(self, key)

        for key in files:
            path_or_url = getattr(self, key, None)
            if path_or_url:
                value = self.make_file_url(path_or_url)
                url_key = key + '_url'
                rv[url_key] = value
            else:
                rv[key] = None
                continue
        for key in additional:
            value = getattr(self, key)
            if isinstance(value, Document):
                rv[key] = value.to_json_dbref()
            elif isinstance(value, dict):
                serialized_value = dict()
                for k, v in value.items():
                    if isinstance(v, Document):
                        serialized_value[k] = v.to_json_dbref()
                    else:
                        serialized_value[k] = v
                rv[key] = serialized_value
            elif not isinstance(value, str) and isinstance(value, collections.Iterable):
                serialized_value = []
                for item in value:
                    if isinstance(item, Document):
                        serialized_value.append(item.to_json_dbref())
                    else:
                        serialized_value.append(item)
                rv[key] = serialized_value
            else:
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

        if for_central:
            rv['_id'] = rv.pop('central_id', None)

        return rv

    def to_json_dbref(self, for_central=False):
        fields = self.__json_dbref__ or []
        renames = self.__json_rename__ or dict()

        rv = dict()
        if for_central and hasattr(self, 'central_id'):
            rv['_id'] = self.central_id
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
    def _convert_value_from_json(value, key, field, instance, from_central, path_in_instance, unresolved_references, **kwargs):

        if field is None:
            return field.to_python(value)

        ReferenceField = _import_class('ReferenceField')
        GenericReferenceField = _import_class('GenericReferenceField')
        EmbeddedDocumentField = _import_class('EmbeddedDocumentField')
        ListField = _import_class('ListField')

        ## ReferenceField: convert reference to use the local ``id`` instead of the central one.
        if isinstance(field, ReferenceField):
            if isinstance(value, dict):
                value = field.to_python(value['_id'])
            document_id = value.id
            if from_central:
                try:
                    document = field.document_type_obj.objects.get(central_id=document_id)
                    return document
                except Exception as e:
                    from MookAPI.sync import UnresolvedReference
                    ref = UnresolvedReference()
                    ref.field_path = path_in_instance
                    ref.class_name = field.document_type_obj.__name__
                    ref.central_id = document_id
                    unresolved_references.append(ref)
                    return value # We keep an invalid DBRef as a placeholder
            else:
                try:
                    document = field.document_type_obj.objects.get(id=document_id)
                    return document
                except Exception as e:
                    return value # We keep an invalid DBRef as a placeholder

        ## GenericField: convert reference to use the local ``id`` instead of the central one.
        elif isinstance(field, GenericReferenceField):
            # FIXME This way of getting the id is not really clean.
            value = field.to_python(value['_id'])
            document_id = value.id
            try:
                from MookAPI.helpers import get_service_for_class
                service = get_service_for_class(value['_cls'])
                document = service.get(central_id=document_id)
                return document
            except:
                from MookAPI.sync import UnresolvedReference
                ref = UnresolvedReference()
                ref.field_path = path_in_instance
                ref.class_name = field.document_type_obj.__name__
                ref.central_id = value['_id']
                unresolved_references.append(ref)
                return value # We keep an invalid DBRef as a placeholder

        ## EmbeddedDocumentField: instantiate MongoCoderEmbeddedDocument from JSON
        elif isinstance(field, EmbeddedDocumentField):
            return field.document_type_obj.from_json(
                value,
                from_central=from_central,
                path_in_instance=path_in_instance,
                instance=instance,
                unresolved_references=unresolved_references,
                **kwargs
            )

        ## ListField: recursively convert all elements in the list
        elif isinstance(field, ListField):
            converted_value = []
            for index, element in enumerate(value):
                # FIXME This next_path does not seem right.
                next_path_in_instance = "%s[%d]" % (path_in_instance, index)
                value = JsonSerializer._convert_value_from_json(
                    value=element,
                    key=key,
                    field=field.field,
                    instance=instance,
                    from_central=from_central,
                    path_in_instance=next_path_in_instance,
                    unresolved_references=unresolved_references,
                    **kwargs
                )
                converted_value.append(value)

            return converted_value

        else:
            return field.to_python(value)

    def _set_value_from_json(self, json, key, instance, **kwargs):

        from_central = kwargs.pop('from_central', False)
        path_in_instance = kwargs.pop('path_in_instance', '')
        unresolved_references = kwargs.pop('unresolved_references', [])
        upload_path = kwargs.get('upload_path', '/tmp/')

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
        StringField = _import_class('StringField')

        if isinstance(field, FileField):
            url_key = key + '_url'
            filename_key = key + '_filename'
            url = json[url_key]
            filename = os.path.join(upload_path, "tmp", json[filename_key] or 'temp')
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

        elif key in (self.__json_files__ or []) and isinstance(field, StringField):
            url_key = key + '_url'
            if url_key in json:
                url = json[url_key]
                filename = value # FIXME If the value is an absolute URL, extract the filename
                path = os.path.join(upload_path, filename)
                with open(path, 'wb') as handle:
                    r = requests.get(url, stream=True)
                    if not r.ok:
                        return  # Raise an exception
                    for block in r.iter_content(1024):
                        if not block:
                            break
                        handle.write(block)
                setattr(self, key, value)

        else:
            value = self._convert_value_from_json(
                value=value,
                key=key,
                field=field,
                instance=instance,
                from_central=from_central,
                path_in_instance=path_in_instance,
                unresolved_references=unresolved_references,
                **kwargs
            )
            setattr(self, key, value)

    @classmethod
    def from_json(cls, json, **kwargs):

        from_central = kwargs.pop('from_central', False)
        overwrite_document = kwargs.pop('overwrite_document', None)
        instance = kwargs.pop('instance', None)
        path_in_instance = kwargs.pop('path_in_instance', '')
        unresolved_references = kwargs.pop('unresolved_references', [])

        obj = cls()

        if not instance:
            instance = obj

        Document = _import_class('Document')
        if from_central and issubclass(cls, Document):
            json['central_id'] = json.pop('_id')

        for key in json.iterkeys():
            next_path_in_instance = ("%s.%s" % (path_in_instance, key)).lstrip(".")
            obj._set_value_from_json(
                json=json,
                key=key,
                instance=instance,
                from_central=from_central,
                path_in_instance=next_path_in_instance,
                unresolved_references=unresolved_references,
                **kwargs
            )

        obj.unresolved_references = unresolved_references

        if overwrite_document:
            obj.id = overwrite_document.id

        return obj

    def set_value_for_field_path(self, value, field_path):
        import re
        def rec_set(obj, path, value):
            path_parts = path.split('.')
            key = path_parts.pop(0)

            match = re.match("^(\w+)\[(\d+)\]$", key)
            if match:
                key = match.group(1)
                index = int(match.group(2))
                tab = getattr(obj, key, None)
                if path_parts:
                    new_path = ".".join(path_parts)
                    sub_obj = rec_set(tab[index], new_path, value)
                    tab[index] = sub_obj
                    setattr(obj, key, tab)
                    return obj
                else:
                    tab[index] = value
                    setattr(obj, key, tab)
                    return obj
            else:
                if path_parts:
                    new_obj = getattr(obj, key)
                    new_path = ".".join(path_parts)
                    sub_obj = rec_set(new_obj, new_path, value)
                    setattr(obj, key, sub_obj)
                    return obj
                else:
                    setattr(obj, key, value)
                    return obj

        return rec_set(self, field_path, value)


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

Document = _import_class('Document')
ObjectIdField = _import_class('ObjectIdField')
DateTimeField = _import_class('DateTimeField')

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
    A CSV writer which will yield rows which is encoded
    in the given encoding.
    """

    def __init__(self, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.encoding = encoding

    def csv_object_serialize(self, o):
        if isinstance(o, CsvSerializer):
            csv_data, is_list = o.to_csv()
            if is_list:
                return self.csv_rows_serialize(csv_data)
            else:
                return self.csv_row_serialize(csv_data)

    def csv_row_serialize(self, row):
        self.writer.writerow([s.encode(self.encoding) for s in row])
        data = self.queue.getvalue()
        self.queue.truncate(0)
        return data

    def csv_rows_serialize(self, rows):
        return "".join(self.csv_row_serialize(row) for row in rows)
