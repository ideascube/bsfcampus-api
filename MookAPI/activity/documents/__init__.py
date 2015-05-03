from MookAPI import db
import datetime
import bson
from slugify import slugify
import MookAPI.mongo_coder as mc


class Activity(mc.SyncableDocument):
	"""Describes any kind of user activity."""

	meta = {
		'allow_inheritance': True,
		'abstract': True
	}

	### PROPERTIES

	# user = db.ReferenceField('User', required=True)
	# """The user performing the activity."""

	date = db.DateTimeField(default=datetime.datetime.now, required=True)
	"""The date at which the activity was performed."""
