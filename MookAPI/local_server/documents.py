import flask
from MookAPI import db
import datetime
import bson
from MookAPI.users.documents import User

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

	@property
	def url(self):
		raise exceptions.NotImplementedError("This object class has no URL defined.")

	def save(self, *args, **kwargs):
		self.last_modification = datetime.datetime.now()
		return super(SyncableDocument, self).save(*args, **kwargs)

	def reference(self):
		obj = {}
		obj['_cls'] = type(self).__name__
		obj['_ref'] = self.to_dbref()
		obj['url'] = self.url
		return obj

	# @if_central
	def items_to_sync(self, last_sync):

		if last_sync is None or self.last_modification is None or last_sync < self.last_modification:
			return [self.reference()]

		return []


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
