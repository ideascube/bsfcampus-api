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

	## Question text
	question_text = db.StringField(required=True)

	## Right propositions
	right_propositions = db.ListField(db.EmbeddedDocumentField(MultipleAnswerMCQExerciseQuestionProposition))

	## Wrong propositions
	wrong_propositions = db.ListField(db.EmbeddedDocumentField(MultipleAnswerMCQExerciseQuestionProposition))

	def without_answer(self):
		son = self.to_mongo()
		son['propositions'] = son['right_propositions'] + son['wrong_propositions']
		son['right_propositions'] = None
		son['wrong_propositions'] = None
		shuffle(son['propositions'])
		return son


class MultipleAnswerMCQExerciseQuestionAnswer(ExerciseQuestionAnswer):
	"""Answers given to a multiple-answer MCQ."""

	## The list of chosen propositions, identified by their ObjectIds
	given_propositions = db.ListField(db.ObjectIdField())

	def init_with_data(data):
		self.given_propositions = []
		for proposition in data['propositions']:
			self.given_propositions.append(ObjectId(proposition))
		return self

	def is_correct(self, question):
		expected_propositions = set(map(lambda rp: rp._id, question.right_propositions))
		return expected_propositions == set(self.given_propositions)
