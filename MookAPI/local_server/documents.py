import flask
from MookAPI import db
import datetime
import bson
from MookAPI.users.documents import User

class SyncableItem(db.EmbeddedDocument):
	"""
	Each local server contains a list of items to synchronize
	"""

	### PROPERTIES

	## Date of last synchronization
	last_sync = db.DateTimeField(default=datetime.datetime.now)

	## The item to synchronize
	item = db.GenericReferenceField()

	### METHODS

	def sync_list(self):
		"""
		This method requires every "syncable" item to implement "items_to_sync".
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
