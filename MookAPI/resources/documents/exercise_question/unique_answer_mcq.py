from MookAPI import db
import datetime
from bson import ObjectId
from . import ExerciseQuestion, ExerciseQuestionAnswer
from random import shuffle


class UniqueAnswerMCQExerciseQuestionProposition(db.EmbeddedDocument):
	"""Stores a proposition to a unique-answer MCQ."""

	## Object Id
	_id = db.ObjectIdField(default=ObjectId)

	## Text
	text = db.StringField()


class UniqueAnswerMCQExerciseQuestion(ExerciseQuestion):
	"""Multiple choice question with one possible answer only."""

	## Propositions
	propositions = db.ListField(db.EmbeddedDocumentField(UniqueAnswerMCQExerciseQuestionProposition))

	## Correct answer
	correct_answer = db.ObjectIdField()


class UniqueAnswerMCQExerciseQuestionAnswer(ExerciseQuestionAnswer):
	"""Answer given to a unique-answer MCQ."""

	## The chosen propositions, identified by its ObjectId
	given_proposition = db.ObjectIdField()

	def init_with_data(self, data):
		self.given_proposition = ObjectId(data['proposition'])
		return self

	def is_correct(self, question):
		return self.given_propositions == question.right_proposition._id
