import os
import pkgutil
import importlib
import requests
from bson import json_util

from mongoengine.common import _import_class

from flask import Blueprint
from flask.json import JSONEncoder as BaseJSONEncoder
from .core import db


def register_blueprints(app, package_name, package_path):
    rv = []
    for _, name, _ in pkgutil.iter_modules(package_path):
        m = importlib.import_module('%s.%s' % (package_name, name))
        for item in dir(m):
            item = getattr(m, item)
            if isinstance(item, Blueprint):
                app.register_blueprint(item)
            rv.append(item)
    return rv


class JsonSerializer(object):

    __json_public__ = None
    __json_hidden__ = None
    __json_additional__ = None
    __json_modifiers__ = None
    __json_rename__ = None
    __json_dbref__ = None

    def encode_mongo(self, fields=None):

        Document = _import_class('Document')
        EmbeddedDocument = _import_class('EmbeddedDocument')

        if not isinstance(self, (Document, EmbeddedDocument)):
            raise TypeError("This object is not a MongoEngine (embedded) document.")

        FileField = _import_class('FileField')
        EmbeddedDocumentField = _import_class('EmbeddedDocumentField')
        ListField = _import_class('ListField')
        ReferenceField = _import_class('ReferenceField')

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

                elif isinstance(field, ReferenceField):
                    value = getattr(self, key, None)
                    if value:
                        rv[key] = value.to_json_dbref()

                ## Recursively encode embedded documents....
                elif isinstance(field, EmbeddedDocumentField):
                    if issubclass(field.document_type_obj, JsonSerializer):
                        value = getattr(self, key, None)
                        if value:
                            rv[key] = value.to_json()

                ## ...or lists thereof.
                elif isinstance(field, ListField):
                    if isinstance(field.field, EmbeddedDocumentField):
                        if issubclass(field.field.document_type_obj, JsonSerializer):
                            values = getattr(self, key, [])
                            rv[key] = [value.to_json() for value in values]
                    elif isinstance(field.field, ReferenceField):
                        values = getattr(self, key, [])
                        rv[key] = [value.to_json_dbref() for value in values]

        return rv

    def get_field_names(self):
        Document = _import_class('Document')
        EmbeddedDocument = _import_class('EmbeddedDocument')
        if isinstance(self, (Document, EmbeddedDocument)):
            return self._fields.keys()
        elif self.__dict__:
            return self.__dict__.keys()
        return []

    def to_json(self):
        field_names = self.get_field_names()

        public = self.__json_public__ or field_names
        hidden = self.__json_hidden__ or []
        additional = self.__json_additional__ or []
        modifiers = self.__json_modifiers__ or dict()
        renames = self.__json_rename__ or dict()

        Document = _import_class('Document')
        EmbeddedDocument = _import_class('EmbeddedDocument')
        if isinstance(self, (Document, EmbeddedDocument)):
            rv = self.encode_mongo(fields=public)
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

        return rv

    def to_json_dbref(self):
        fields = self.__json_dbref__ or []
        renames = self.__json_rename__ or dict()

        rv = dict()
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
    def _convert_value_from_json(value, field):

        ReferenceField = _import_class('ReferenceField')
        EmbeddedDocumentField = _import_class('EmbeddedDocumentField')
        ListField = _import_class('ListField')

        ## ReferenceField: convert reference to use the local ``id`` instead of the distant one.
        if isinstance(field, ReferenceField):
            # FIXME This way of getting the id is not really clean.
            value = field.to_python(value['_id'])
            document_id = value.id
            document = field.document_type_obj.objects(distant_id=document_id).first()
            return document

        ## EmbeddedDocumentField: instantiate MongoCoderEmbeddedDocument from JSON
        elif isinstance(field, EmbeddedDocumentField):
            return field.document_type_obj.from_json(value)

        ## ListField: recursively convert all elements in the list
        elif isinstance(field, ListField):
            ## field.field is the type of elements in the listfield
            if field.field is None:
                return field.to_python(value)

            converted_value = []
            for element in value:
                converted_element = JsonSerializer._convert_value_from_json(element, field.field)
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
            os.remove(filename)
        ## Any other type: convert value before setting using setattr
        else:
            value = self._convert_value_from_json(value, field)
            setattr(self, key, value)

    @classmethod
    def from_json(cls, json, distant=False):
        obj = cls()

        for key in json.iterkeys():
            obj._set_value_from_json(json, key)

        if distant:
            obj.distant_id = obj.id
            obj.id = None

        return obj


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
