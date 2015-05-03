import flask
from MookAPI import db
import datetime
import bson
from mongoengine.common import _import_class
import requests
import os, sys

class MongoCoderMixin(object):

	def encode_mongo(self, instance=None):

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
					if hasattr(self, url_key):
						getattr(self, url_key)
						son[url_key] = getattr(self, url_key)
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
	def convert_value_from_json(value, field):

		ReferenceField = _import_class('ReferenceField')
		EmbeddedDocumentField = _import_class('EmbeddedDocumentField')
		ListField = _import_class('ListField')

		if isinstance(field, ReferenceField):
			value = field.to_python(value)
			return field.document_type_obj.objects(distant_id=value.id).first()

		elif isinstance(field, EmbeddedDocumentField):
			return field.document_type_obj.decode_mongo(value)

		elif isinstance(field, ListField):
			## field.field is the type of elements in the listfield
			if field.field is None:
				return field.to_python(value)

			converted_value = []
			for element in value:
				converted_element = MongoCoderMixin.convert_value_from_json(element, field.field)
				converted_value.append(converted_element)
			
			return converted_value

		else:
			return field.to_python(value)

	def set_value_from_json(self, json, key):

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
					return # Raise an exception
				for block in r.iter_content(1024):
					if not block:
						break
					handle.write(block)
			value = open(filename, 'rb')
			
			self[key].put(value, content_type=r.headers['content-type'], filename=filename)
			os.remove(filename)
		## Any other type: convert value before setting using setattr
		else:
			value = self.convert_value_from_json(value, field)
			setattr(self, key, value)


class MongoCoderDocument(db.Document, MongoCoderMixin):

	meta = {
		'allow_inheritance': True,
		'abstract': True
	}

	@property
	def url(self):
		raise exceptions.NotImplementedError("The single-object URL of this document class is not defined.")

	@classmethod
	def json_key(cls):
		return cls.__name__.lower()

	@classmethod
	def json_key_collection(cls):
		return cls.json_key() + 's'

	def reference(self):
		son = {}
		son['_cls'] = type(self).__name__
		son['_ref'] = self.to_dbref()
		son['url'] = self.url
		return son

	@classmethod
	def decode_mongo(cls, json):
		obj = cls()
		
		for key in json.iterkeys():
			obj.set_value_from_json(json, key)
				
		return obj

	@classmethod
	def decode_json_result(cls, json):
		return cls.decode_mongo(json[cls.json_key()])

class MongoCoderEmbeddedDocument(db.EmbeddedDocument, MongoCoderMixin):

	meta = {
		'allow_inheritance': True,
		'abstract': True
	}

	@classmethod
	def decode_mongo(cls, json):
		obj = cls()
		
		for key in json.iterkeys():
			obj.set_value_from_json(json, key)
				
		return obj

class DeletedSyncableDocument(MongoCoderDocument):

	document = db.GenericReferenceField()

	top_level_document = db.GenericReferenceField()

	date = db.DateTimeField()

	def save(self, *args, **kwargs):
		self.top_level_document = self.document.top_level_syncable_document()
		if self.date is None:
			self.date = datetime.datetime.now()
		return super(DeletedSyncableDocument, self).save(*args, **kwargs)


## All documents that need to be synced must inherit from this class.
class SyncableDocument(MongoCoderDocument):
	"""
	This document type must be the base class of any document that wants to be a syncable item.
	They should override, if needed, the 'items_to_sync' method.
	"""

	meta = {
		'allow_inheritance': True,
		'abstract': True
	}

	## Last modification
	last_modification = db.DateTimeField()

	## Id of the document on the central server
	distant_id = db.ObjectIdField()

	def top_level_syncable_document(self):
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
		return [self.reference()]

	def items_to_update(self, last_sync):
		if last_sync is None or self.last_modification is None or last_sync < self.last_modification:
			return [self.reference()]

		return []

	def items_to_delete(self, last_sync):
		items = []

		for obj in DeletedSyncableDocument.objects.filter(top_level_document=self.top_level_syncable_document()):
			if last_sync is None or obj.date is None or last_sync < obj.date:
				document = obj.encode_mongo()['document']
				items.append(document)

		return items

	def items_to_sync(self, last_sync):
		items = {}
		items['update'] = self.items_to_update(last_sync)
		items['delete'] = self.items_to_delete(last_sync)
		## We should do some cleanup at this point, in particular remove deletable items from 'update' list.
		return items

	@classmethod
	def decode_mongo(cls, mongo):
		obj = super(SyncableDocument, cls).decode_mongo(mongo)

		print "Decoding mongo", mongo
		obj.distant_id = mongo['_id']
				
		return obj
