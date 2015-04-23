from MookAPI import db
from bson import ObjectId
from . import ExerciseQuestion, ExerciseQuestionAnswer
from random import shuffle


class OrderingExerciseQuestionItem(db.EmbeddedDocument):
	"""Stores an item for the overall ordering question."""

	## Object Id
	_id = db.ObjectIdField(default=ObjectId)

	## Text
	text = db.StringField()


class OrderingExerciseQuestion(ExerciseQuestion):
	"""A list of items that need to be ordered. May be horizontal or vertical"""

	## Object Id
	_id = db.ObjectIdField(default=ObjectId)

	## Propositions
	items = db.ListField(db.EmbeddedDocumentField(OrderingExerciseQuestionItem))

	def without_correct_answer(self):
		son = super(OrderingExerciseQuestion, self).without_correct_answer()
		shuffle(son['items'])
		return son

	def answer_with_data(self, data):
		return OrderingExerciseQuestionAnswer().init_with_data(data)

	def getItemsById(self, itemsId):
		result = [];
		for item in self.items:
			print(str(item._id))
			if item._id in itemsId:
				result.append(item)
		return result



class OrderingExerciseQuestionAnswer(ExerciseQuestionAnswer):
	"""Ordered items given for this ordering question."""

	## The given propositions, identified by their ObjectIds
	given_ordered_items = db.ListField(db.ObjectIdField())

	def init_with_data(self, data):
		self.given_ordered_items = data.getlist('given_ordered_items[]')
		print(self.given_ordered_items)
		return self

	def is_correct(self, question, parameters):
		ordered_items = question.getItemsById(self.given_ordered_items)
		correct_ordered_items = question.items
		return ordered_items == correct_ordered_items
