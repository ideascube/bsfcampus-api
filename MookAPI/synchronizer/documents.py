import flask
from MookAPI import db
import datetime
import bson

class ItemToSync(db.Document):

	### PROPERTIES

	## Reference to the DISTANT object
	reference = db.GenericReferenceField()

	## Action to perform (delete local or fetch new version of distant)
	action = db.StringField(choices=('update', 'delete'))

	## URL to fetch update info (null if action == 'delete')
	url = db.StringField()
