from MookAPI import db
import datetime
import exceptions
from . import *
from exercise_question import *
from random import shuffle
from bson import ObjectId
import exceptions


class ExerciseResourceContent(ResourceContent):
	"""An exercise with a list of questions."""

	## Embedded list of questions
	questions = db.ListField(db.EmbeddedDocumentField(ExerciseQuestion))


class ExerciseResource(Resource):
	resource_content = db.EmbeddedDocumentField(ExerciseResourceContent)

	number_of_questions = db.IntField();

	max_mistakes = db.IntField();

	def questions(self):
		return self.resource_content.questions

	def question(self, question_id):
		oid = ObjectId(question_id)
		for question in self.questions():
			if question._id == oid:
				return question
		raise exceptions.KeyError("Question not found.")

	def random_questions(self, number):
		all_questions = self.questions()
		shuffle(all_questions)
		return all_questions[:number]
