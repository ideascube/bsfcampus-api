from MookAPI import db
import datetime
from .base import ExerciseQuestion

class MultipleAnswerMCQExerciseQuestion(ExerciseQuestion):
	"""Multiple choice question with several possible answers."""

	## Question text
	question_text = db.StringField(required=True)

	## Right answers
	right_answers = db.ListField(db.StringField())

	## Wrong answers
	wrong_answers = db.ListField(db.StringField())
