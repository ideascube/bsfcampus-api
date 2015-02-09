from MookAPI import db
import datetime

class ExerciseQuestion(db.DynamicEmbeddedDocument):
	"""Generic collection, every question type will inherit from this."""
	
	meta = {
		'allow_inheritance': True,
		'abstract': True
	}