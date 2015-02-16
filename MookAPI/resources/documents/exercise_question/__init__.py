from MookAPI import db
from bson import ObjectId
import datetime
import exceptions


class ExerciseQuestion(db.DynamicEmbeddedDocument):
	"""
	Generic collection, every question type will inherit from this.
	Subclasses should override method "without_answer" in order to define the version sent to clients.
	"""
	
	meta = {
		'allow_inheritance': True,
		'abstract': True
	}

	_id = db.ObjectIdField(default=ObjectId)


__all__ = [
	'ExerciseQuestion',
	'multiple_answer_mcq',
	'unique_answer_mcq'
]
