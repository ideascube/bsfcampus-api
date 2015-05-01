import flask
from MookAPI import db
import datetime
import bson
from MookAPI.users.documents import User
from mongoengine.common import _import_class
import requests
import os, sys

class DeletedSyncableDocument(db.Document):

	document = db.GenericReferenceField()

	top_level_document = db.GenericReferenceField()

	date = db.DateTimeField()

	def save(self, *args, **kwargs):
		self.top_level_document = self.document.top_level_syncable_document()
		if self.date is None:
			self.date = datetime.datetime.now()
		return super(DeletedSyncableDocument, self).save(*args, **kwargs)


class SyncableDocumentJSONParserMixin(object):
	def convert_value_from_json(self, value, field):

		ReferenceField = _import_class('ReferenceField')
		EmbeddedDocumentField = _import_class('EmbeddedDocumentField')
		ListField = _import_class('ListField')

		if isinstance(field, ReferenceField):
			value = field.to_python(value)
			return field.document_type_obj.objects(distant_id=value.id).first()

		elif isinstance(field, EmbeddedDocumentField):
			return field.document_type_obj.init_with_json_object(value)

		elif isinstance(field, ListField):
			## field.field is the type of elements in the listfield
			if field.field is None:
				return field.to_python(value)

			converted_value = []
			for element in value:
				converted_element = self.convert_value_from_json(element, field.field)
				converted_value.append(converted_element)
			
			return converted_value

		else:
			return field.to_python(value)

	def set_value_from_json(self, json, key):

		## Get value from json
		value = json[key]
		if value is None:
			return

		## Check if key is valid and has associated Field object
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
			url = json[url_key]
			with open('temp', 'wb') as handle:
				r = requests.get(url, stream=True)
				if not r.ok:
					return # Raise an exception
				for block in r.iter_content(1024):
					if not block:
						break
					handle.write(block)
			value = open('temp', 'rb')
			try:
				self[key].put(value, content_type=r.headers['content-type'])
				os.remove('temp')
			except:
				print sys.exc_info()
		## Defer all other field types to dedicated method.
		else:
			value = self.convert_value_from_json(value, field)
			setattr(self, key, value)


## All documents that need to be synced must inherit from this class.
class SyncableDocument(db.Document, SyncableDocumentJSONParserMixin):
	"""
	This document type must be the base class of any document that wants to be a syncable item.
	Subclasses must implement the 'url' virtual property.
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

	@property
	def url(self):
		raise exceptions.NotImplementedError("The single-object URL of this document class is not defined.")

	@classmethod
	def json_key(cls):
		return cls.__name__.lower()

	def save(self, *args, **kwargs):
		self.last_modification = datetime.datetime.now()
		return super(SyncableDocument, self).save(*args, **kwargs)

	def delete(self, *args, **kwargs):
		reference = DeletedSyncableDocument()
		reference.document = self
		reference.save()
		return super(SyncableDocument, self).delete(*args, **kwargs)

	def reference(self):
		obj = {}
		obj['_cls'] = type(self).__name__
		obj['_ref'] = self.to_dbref()
		obj['url'] = self.url
		return obj

	def all_syncable_items(self):
		return [self.reference()]

	def items_to_update(self, last_sync):
		items = []

		if last_sync is None or self.last_modification is None or last_sync < self.last_modification:
			items.append(self.reference())

		return items

	def items_to_delete(self, last_sync):
		items = []

		for obj in DeletedSyncableDocument.objects.filter(top_level_document=self.top_level_syncable_document()):
			if last_sync is None or obj.date is None or last_sync < obj.date:
				items.append(obj.to_mongo()['document'])

		return items

	def items_to_sync(self, last_sync):
		items = {}
		items['update'] = self.items_to_update(last_sync)
		items['delete'] = self.items_to_delete(last_sync)
		# We should do some cleanup at this point, in particular remove deletable items from 'update' list.
		return items

	@classmethod
	def init_with_json_object(cls, json):
		print "Creating document with json", json
		obj = cls()
		
		for key in json.iterkeys():
			obj.set_value_from_json(json, key)

		obj.distant_id = json['_id']
				
		return obj

	@classmethod
	def init_with_json_result(cls, json):
		return cls.init_with_json_object(json[cls.json_key()])

class SyncableEmbeddedDocument(db.EmbeddedDocument, SyncableDocumentJSONParserMixin):

	meta = {
		'allow_inheritance': True,
		'abstract': True
	}

	@classmethod
	def init_with_json_object(cls, json):
		print "Creating embedded document with json", json
		obj = cls()

		for key in json.iterkeys():
			obj.set_value_from_json(json, key)
				
		return obj


class SyncableItem(db.EmbeddedDocument):
	"""
	This embedded document contains a reference to an item (document) to synchronize, and the date it was last checked out by the local server.
	"""

	### PROPERTIES

	## Date of last synchronization
	last_sync = db.DateTimeField()

	## The item to synchronize
	## Any item referenced in this field must be a subclass of SyncableDocument
	item = db.GenericReferenceField()

	### METHODS

	def sync_list(self):
		"""
		This method finds the list of atomic documents the local server has to sync for the current "item" to be synced.
		"""
		return self.item.items_to_sync(self.last_sync)


class LocalServer(db.Document):
	"""
	This collection contains the list of all central servers connected to the current central server.
	"""

	### PROPERTIES

	## Each local server has a (kind of) standard user account, referenced here
	user = db.ReferenceField(User, unique=True)

	## List of items to syncronize
	syncable_items = db.ListField(db.EmbeddedDocumentField(SyncableItem))
