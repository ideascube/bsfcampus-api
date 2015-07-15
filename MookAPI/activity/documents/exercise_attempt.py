from bson import ObjectId

from MookAPI.core import db
from MookAPI.helpers import JsonSerializer
from . import ActivityJsonSerializer, Activity
from MookAPI.resources.documents.exercise_question import ExerciseQuestionAnswer


class ExerciseAttemptQuestionAnswerJsonSerializer(JsonSerializer):
    pass


class ExerciseAttemptQuestionAnswer(ExerciseAttemptQuestionAnswerJsonSerializer, db.EmbeddedDocument):
    """
    Stores the data relative to one answer in an attempt to an exercise, including the answer given.
    """

    ### PROPERTIES

    question_id = db.ObjectIdField()
    """A unique identifier for the question."""

    parameters = db.DynamicField()
    """A dynamic object to store any parameters needed to present the question."""

    given_answer = db.EmbeddedDocumentField(ExerciseQuestionAnswer)
    """An embedded document to store the given answer to the question."""

    is_answered_correctly = db.BooleanField()
    """Whether the `given_answer` is correct."""

    ### METHODS

    @classmethod
    def init_with_question(cls, question):
        """Instantiate an object to store the answer given to a question."""

        obj = cls()
        obj.question_id = question._id

        return obj

    def is_answered(self):
        return self.given_answer is not None


class ExerciseAttemptJsonSerializer(ActivityJsonSerializer):
    @staticmethod
    def question_answers_modifier(son, exercise_attempt):
        for (index, qa) in enumerate(exercise_attempt.question_answers):
            question = exercise_attempt.exercise.question(qa.question_id)
            if qa.given_answer is not None:
                son[index]['question'] = question.with_computed_correct_answer(qa.parameters)
            else:
                son[index]['question'] = question.without_correct_answer()
                break

        return son

    __json_additional__ = []
    __json_additional__.extend(ActivityJsonSerializer.__json_additional__ or [])
    __json_additional__.extend(['max_mistakes', 'fail_linked_resource'])

    __json_modifiers__ = dict()
    __json_modifiers__.update(ActivityJsonSerializer.__json_modifiers__ or dict())
    __json_modifiers__.update(
        dict(
            question_answers=question_answers_modifier.__func__
        )
    )


class ExerciseAttempt(ExerciseAttemptJsonSerializer, Activity):
    """
    Records any attempt at an exercise.
    """

    ### PROPERTIES

    ## Exercise
    exercise = db.ReferenceField('ExerciseResource')

    ## Question answers
    question_answers = db.ListField(db.EmbeddedDocumentField(ExerciseAttemptQuestionAnswer))

    ## Is exercise validated
    is_validated = db.BooleanField(default=False)

    @property
    def max_mistakes(self):
        return self.exercise.resource_content.max_mistakes

    @property
    def fail_linked_resource(self):
        if self.exercise.resource_content.fail_linked_resource:
            return self.exercise.resource_content.fail_linked_resource
        return None

    ### METHODS

    @classmethod
    def init_with_exercise(cls, exercise):
        """Initiate an attempt for a given exercise."""
        obj = cls()
        obj.exercise = exercise

        questions = exercise.random_questions()
        obj.question_answers = [ExerciseAttemptQuestionAnswer.init_with_question(q) for q in questions]

        return obj

    def __unicode__(self):
        if self.exercise is not None:
            return self.exercise.title
        return self.id

    def question_answer(self, question_id):
        oid = ObjectId(question_id)
        for question_answer in self.question_answers:
            if question_answer.question_id == oid:
                return question_answer
        raise KeyError("Question not found.")

    def set_question_answer(self, question_id, question_answer):
        oid = ObjectId(question_id)
        for (index, qa) in enumerate(self.question_answers):
            if qa.question_id == oid:
                self.question_answers[index] = question_answer
                return question_answer
        raise KeyError("Question not found.")

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

    def is_exercise_completed(self):
        nb_total_questions = self.exercise.resource_content.number_of_questions
        nb_max_mistakes = self.exercise.resource_content.max_mistakes
        answered_questions = filter(lambda a: a.given_answer is not None, self.question_answers)
        if len(answered_questions) >= nb_total_questions:
            right_answers = filter(lambda a: a.is_answered_correctly, answered_questions)
            if len(right_answers) >= nb_total_questions - nb_max_mistakes:
                return True

        return False
