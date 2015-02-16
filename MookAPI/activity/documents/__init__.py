from MookAPI import db
import datetime
import bson
from slugify import slugify


class Activity(db.Document):
	meta = {
		'allow_inheritance': True,
		'abstract': True
	}

	### PROPERTIES

	## User
	# user = db.ReferenceField('User', required=True)

	## Date
	date = db.DateTimeField(default=datetime.datetime.now, required=True)
