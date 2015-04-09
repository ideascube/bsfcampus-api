from MookAPI import db, params
from . import Activity
from MookAPI.resources.documents.exercise import ExerciseResource
from MookAPI.resources.documents.exercise_question import ExerciseQuestionAnswer
from random import shuffle
from bson import ObjectId
import exceptions


class ExerciseAttemptQuestionAnswer(db.EmbeddedDocument):
	"""
	Stores the data relative to one answer in an attempt to an exercise, including the answer given.
	"""

	### PROPERTIES

	## The ObjectId of the question.
	## The question is an embedded document so this is not a ReferenceField.
	question_id = db.ObjectIdField()

	## Parameters
	## If the question has several possible modalities, they can be set here.
	parameters = db.DynamicField()

	## The answer given; 
	given_answer = db.EmbeddedDocumentField(ExerciseQuestionAnswer)

	## Whether the answer is correct.
	is_answered_correctly = db.BooleanField()

	### METHODS

	## Hack to bypass __init__ which I could not figure out how to use just now.
	def init_with_question(self, question):
		"""Initiate an object to store the answer given to a question."""

		self.question_id = question._id
		
		## Some question types may have parameters, they can be generated here:
		# self.parameters = question.generate_parameters()

		return self

	def is_answered(self):
		return self.given_answer is not None


class ExerciseAttempt(Activity):
	"""
	Records any attempt at an exercise.
	"""
	
	### PROPERTIES

	## Exercise
	exercise = db.ReferenceField(ExerciseResource)
	
	## Question answers
	question_answers = db.ListField(db.EmbeddedDocumentField(ExerciseAttemptQuestionAnswer))

	### METHODS

	## Hack to bypass __init__ which I could not figure out how to use just now.
	def init_with_exercise(self, exercise):
		"""Initiate an attempt for a given exercise."""
		self.exercise = exercise

		questions = exercise.random_questions(exercise.number_of_questions)
		self.question_answers = map(lambda q: ExerciseAttemptQuestionAnswer().init_with_question(q), questions)

		return self

	def question_answer(self, question_id):
		oid = ObjectId(question_id)
		for question_answer in self.question_answers:
			if question_answer.question_id == oid:
				return question_answer
		raise exceptions.KeyError("Question not found.")

	def set_question_answer(self, question_id, question_answer):
		oid = ObjectId(question_id)
		for (index, qa) in enumerate(self.question_answers):
			if qa.question_id == oid:
				self.question_answers[index] = question_answer
				return question_answer
		raise exceptions.KeyError("Question not found.")

	def save_answer(self, question_id, data):
		"""
		Saves an answer (ExerciseQuestionAnswer) to a question (referenced by its ObjectId).
		"""

		question = self.exercise.question(question_id)
		attempt_question_answer = self.question_answer(question_id)
		question_answer = question.answer_with_data(data)
		attempt_question_answer.given_answer = question_answer
		attempt_question_answer.is_answered_correctly = question_answer.is_correct(question, attempt_question_answer.parameters)
		self.set_question_answer(question_id, attempt_question_answer)

	def to_mongo_detailed(self):
		son = self.to_mongo()
		son['max_mistakes'] = self.exercise.max_mistakes;
		# Answered questions: include full question with correct answer
		# First unanswered question: include full question without correct answer
		# Subsequent questions: question id only (default)
		for (index, qa) in enumerate(self.question_answers):
			if qa.given_answer is not None:
				son['question_answers'][index]['question'] = self.exercise.question(qa.question_id).with_computed_correct_answer(qa.parameters)
			else:
				son['question_answers'][index]['question'] = self.exercise.question(qa.question_id).without_correct_answer()
				break
		return son

