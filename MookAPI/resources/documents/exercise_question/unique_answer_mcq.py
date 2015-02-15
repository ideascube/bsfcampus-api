from MookAPI import db
import datetime
from .base import ExerciseQuestion

class UniqueAnswerMCQExerciseQuestionAnswer(db.EmbeddedDocument):

	## Object Id
	_id = db.ObjectIdField(default=ObjectId)

	## Text
	text = db.StringField()


class UniqueAnswerMCQExerciseQuestion(ExerciseQuestion):
	"""Multiple choice question with one possible answer only."""

	## Question text
	question_text = db.StringField(required=True)

	## Right answer
	right_answer = db.EmbeddedDocumentField(UniqueAnswerMCQExerciseQuestionAnswer)

	## Wrong answers
	wrong_answers = db.ListField(db.EmbeddedDocumentField(UniqueAnswerMCQExerciseQuestionAnswer))
	