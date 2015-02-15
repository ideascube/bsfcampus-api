from MookAPI import db
from bson import ObjectId
import datetime

class ExerciseQuestion(db.DynamicEmbeddedDocument):
	"""Generic collection, every question type will inherit from this."""
	
	meta = {
		'allow_inheritance': True,
		'abstract': True
	}

	_id = db.ObjectIdField(default=ObjectId)
