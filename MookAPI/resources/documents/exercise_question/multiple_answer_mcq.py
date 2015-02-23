from MookAPI import db
import datetime
from bson import ObjectId
from . import ExerciseQuestion, ExerciseQuestionAnswer
from random import shuffle


class MultipleAnswerMCQExerciseQuestionProposition(db.EmbeddedDocument):
	"""Stores a proposition to a multiple-answer MCQ."""

	## Object Id
	_id = db.ObjectIdField(default=ObjectId)

	## Text
	text = db.StringField()


class MultipleAnswerMCQExerciseQuestion(ExerciseQuestion):
	"""Multiple choice question with several possible answers."""

	## Propositions
	propositions = db.ListField(db.EmbeddedDocumentField(MultipleAnswerMCQExerciseQuestionProposition))

	## Correct answer
	correct_answer = db.ListField(db.ObjectIdField())


class MultipleAnswerMCQExerciseQuestionAnswer(ExerciseQuestionAnswer):
	"""Answers given to a multiple-answer MCQ."""

	## The list of chosen propositions, identified by their ObjectIds
	given_propositions = db.ListField(db.ObjectIdField())

	def init_with_data(self, data):
		self.given_propositions = []
		for proposition in data['propositions']:
			self.given_propositions.append(ObjectId(proposition))
		return self

	def is_correct(self, question):
		expected_propositions = set(map(lambda rp: rp._id, question.correct_answer))
		return expected_propositions == set(self.given_propositions)
