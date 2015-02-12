from MookAPI import db
import datetime
from . import *
from exercise_question.base import *

class ExerciseResourceContent(ResourceContent):
	"""An exercise with a list of questions."""

	## Embedded list of questions
	questions = db.ListField(db.EmbeddedDocumentField(ExerciseQuestion))

class ExerciseResource(Resource):
	resource_content = db.EmbeddedDocumentField(ExerciseResourceContent)
