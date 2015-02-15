from MookAPI import db
import datetime
from bson import ObjectId
from .base import ExerciseQuestion

class MultipleAnswerMCQExerciseQuestionAnswer(db.EmbeddedDocument):

	## Object Id
	_id = db.ObjectIdField(default=ObjectId)

	## Text
	text = db.StringField()


class MultipleAnswerMCQExerciseQuestion(ExerciseQuestion):
	"""Multiple choice question with several possible answers."""

	## Question text
	question_text = db.StringField(required=True)

	## Right answers
	right_answers = db.ListField(db.EmbeddedDocumentField(MultipleAnswerMCQExerciseQuestionAnswer))

	## Wrong answers
	wrong_answers = db.ListField(db.EmbeddedDocumentField(MultipleAnswerMCQExerciseQuestionAnswer))
	