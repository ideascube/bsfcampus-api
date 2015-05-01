import flask
from MookAPI import db
import datetime
import bson
from MookAPI.users.documents import User
from mongoengine.common import _import_class
import requests
import os

class DeletedSyncableDocument(db.Document):

	document = db.GenericReferenceField()

	top_level_document = db.GenericReferenceField()

	date = db.DateTimeField()

	def save(self, *args, **kwargs):
		self.top_level_document = self.document.top_level_syncable_document()
		if self.date is None:
			self.date = datetime.datetime.now()
		return super(DeletedSyncableDocument, self).save(*args, **kwargs)


## All documents that need to be synced must inherit from this class.
class SyncableDocument(db.Document):
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
		obj = cls()
		FileField = _import_class('FileField')
		ReferenceField = _import_class('ReferenceField')
		EmbeddedDocumentField = _import_class('EmbeddedDocumentField')
		for key, value in json.iteritems():
			key = obj._reverse_db_field_map.get(key, key)
			if key in obj._fields or key in ('id', 'pk', '_cls'):
				if value is None:
					continue
				field = obj._fields.get(key)
				if not field:
					continue
				elif isinstance(field, FileField):
					url_key = key + '_url'
					url = json[url_key]
					with open('temp', 'wb') as handle:
						r = requests.get(url, stream=True)
						if not r.ok:
							continue
						for block in r.iter_content(1024):
							if not block:
								break
							handle.write(block)
					value = open('temp', 'rb')
					try:
						obj[key].put(value, content_type=r.headers['content-type'])
						os.remove('temp')
					except:
						print sys.exc_info()
				elif isinstance(field, ReferenceField):
					value = field.to_python(value)
					local_ref = field.document_type_obj.objects(distant_id=value.id).first()
					setattr(obj, key, local_ref)
					continue
				elif isinstance(field, EmbeddedDocumentField):
					continue
				else:
					value = field.to_python(value)
					setattr(obj, key, value)
		obj.distant_id = json['_id']
		return obj

	@classmethod
	def init_with_json_result(cls, json):
		return cls.init_with_json_object(json[cls.json_key()])


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
