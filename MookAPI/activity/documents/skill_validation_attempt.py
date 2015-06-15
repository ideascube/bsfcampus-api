__author__ = 'FredFourcade'

import exceptions

import flask
from bson import ObjectId

from MookAPI import db
from . import Activity
from MookAPI.hierarchy.documents.skill_validation import SkillValidationExercise
from exercise_attempt import ExerciseAttemptQuestionAnswer


class SkillValidationAttempt(Activity):
    """
    Records any attempt at an exercise.
    """

    ### PROPERTIES

    ## Exercise
    exercise = db.ReferenceField(SkillValidationExercise)

    ## Question answers
    question_answers = db.ListField(db.EmbeddedDocumentField(ExerciseAttemptQuestionAnswer))

    ### METHODS

    @classmethod
    def init_with_exercise(cls, exercise):
        """Initiate an attempt for a given exercise."""
        obj = cls()
        obj.exercise = exercise

        questions = exercise.random_questions()
        obj.question_answers = map(lambda q: ExerciseAttemptQuestionAnswer.init_with_question(q), questions)

        return obj

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
        attempt_question_answer.is_answered_correctly = question_answer.is_correct(
            question,
            attempt_question_answer.parameters
            )
        self.set_question_answer(question_id, attempt_question_answer)

    def encode_mongo(self):
        son = super(SkillValidationAttempt, self).encode_mongo()

        son['max_mistakes'] = self.exercise.resource_content.max_mistakes
        if self.exercise.resource_content.fail_linked_resource:
            son['fail_linked_resource'] = self.exercise.resource_content.fail_linked_resource.to_mongo()

        ## Answered questions: include full question with correct answer
        ## First unanswered question: include full question without correct answer
        ## Subsequent questions: question id only (default)
        for (index, qa) in enumerate(self.question_answers):
            question = self.exercise.question(qa.question_id)
            if qa.given_answer is not None:
                son['question_answers'][index]['question'] = question.with_computed_correct_answer(qa.parameters)
            else:
                son['question_answers'][index]['question'] = question.without_correct_answer()
                break
        return son

    def is_exercise_completed(self):
        nb_total_questions = self.exercise.resource_content.number_of_questions
        nb_max_mistakes = self.exercise.resource_content.max_mistakes
        answered_questions = filter(lambda a: a.given_answer is not None, self.question_answers)
        if len(answered_questions) >= nb_total_questions:
            right_answers = filter(lambda a: a.is_answered_correctly, answered_questions)
            if len(right_answers) >= nb_total_questions-nb_max_mistakes:
                return True

        return False

