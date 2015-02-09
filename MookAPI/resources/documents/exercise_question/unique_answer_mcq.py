from MookAPI import db
import datetime
from . import *

class UniqueAnswerMCQExerciseQuestion(ExerciseQuestion):
	"""Multiple choice question with one possible answer only."""

	## Question text
	question_text = db.StringField(required=True)

	## Right answer
	right_answer = db.StringField(required=True)

	## Wrong answer
	wrong_answers = db.ListField(db.StringField())
