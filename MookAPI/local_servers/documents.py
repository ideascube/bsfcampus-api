import flask
from MookAPI import db
import datetime
import bson
import MookAPI.mongo_coder as mc
from MookAPI.users.documents import User
from mongoengine.common import _import_class
import requests
import os, sys

class SyncableItem(mc.MongoCoderEmbeddedDocument):
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


class LocalServer(mc.MongoCoderDocument):
	"""
	This collection contains the list of all central servers connected to the current central server.
	"""

	### PROPERTIES

	## Each local server has a (kind of) standard user account, referenced here
	user = db.ReferenceField(User, unique=True)

	## List of items to syncronize
	syncable_items = db.ListField(db.EmbeddedDocumentField(SyncableItem))
