import datetime
from bson import ObjectId, DBRef

from MookAPI.core import db
from MookAPI.serialization import JsonSerializer
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

    asked_date = db.DateTimeField()
    """ The date when the question is asked """

    answered_date = db.DateTimeField()
    """ The date when the question is answered """

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
            if exercise_attempt.exercise and not isinstance(exercise_attempt.exercise, DBRef):
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

    exercise = db.ReferenceField('ExerciseResource')
    """ Exercise """

    @property
    def object(self):
        return self.exercise

    question_answers = db.ListField(db.EmbeddedDocumentField(ExerciseAttemptQuestionAnswer))
    """ Question answers """

    is_validated = db.BooleanField(default=False)
    """ Is exercise validated """

    end_date = db.DateTimeField()
    """ The date when the attempt is ended """

    @property
    def max_mistakes(self):
        if self.exercise and not isinstance(self.exercise, DBRef):
            return self.exercise.resource_content.max_mistakes
        return None

    @property
    def fail_linked_resource(self):
        if self.exercise and not isinstance(self.exercise, DBRef):
            if self.exercise.resource_content.fail_linked_resource:
                return self.exercise.resource_content.fail_linked_resource
        return None

    @property
    def nb_right_answers(self):
        return len(filter(lambda qa: qa.is_answered_correctly, self.question_answers))

    @property
    def nb_questions(self):
        return len(self.question_answers)

    @property
    def duration(self):
        if not self.end_date:
            return None
        else:
            return self.end_date - self.date

    ### METHODS

    @classmethod
    def init_with_exercise(cls, exercise):
        """Initiate an attempt for a given exercise."""
        obj = cls()
        obj.exercise = exercise

        questions = exercise.random_questions()
        obj.question_answers = [ExerciseAttemptQuestionAnswer.init_with_question(q) for q in questions]

        return obj

    def clean(self):
        super(ExerciseAttempt, self).clean()
        self.type = "exercise_attempt"

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
        attempt_question_answer.answered_date = datetime.datetime.now
        self.set_question_answer(question_id, attempt_question_answer)

    def start_question(self, question_id):
        """
        Records the datetime at which the given question has been started
        :param question_id: the id of the question which has just been started
        """
        attempt_question_answer = self.question_answer(question_id)
        attempt_question_answer.asked_date = datetime.datetime.now

    def end(self):
        """
        Records the "now" date as the date when the user has finished the attempt
        """
        self.end_date = datetime.datetime.now

    def is_exercise_validated(self):
        nb_total_questions = len(self.question_answers)
        nb_max_mistakes = self.exercise.resource_content.max_mistakes
        answered_questions = filter(lambda a: a.given_answer is not None, self.question_answers)
        if len(answered_questions) >= nb_total_questions:
            right_answers = filter(lambda a: a.is_answered_correctly, answered_questions)
            if len(right_answers) >= nb_total_questions - nb_max_mistakes:
                return True

        return False

    def is_attempt_completed(self):
        nb_total_questions = len(self.question_answers)
        answered_questions = filter(lambda a: a.given_answer is not None, self.question_answers)
        return len(answered_questions) >= nb_total_questions

    def to_csv_rows(self):
        """ this method all the exercise_attempts data as a list of csv rows """

        rv = []
        for question_answer in self.question_answers:
            csv_fields = self.get_field_names_for_csv()
            question_answer_csv_row_data = self.to_csv_from_field_names(csv_fields)
            question_answer_csv_row_data.append(str(question_answer.question_id))
            exercise = self.exercise
            if isinstance(exercise, DBRef):
                continue
            try:
                question = self.exercise.question(question_answer.question_id)
            except KeyError:
                print "question", question_answer.question_id, "no found in", question_answer
                continue
            question_answer_csv_row_data.append(question.question_heading)
            asked_data = question_answer.asked_date.strftime("%Y-%m-%d %H:%M:%S") if question_answer.asked_date else ""
            question_answer_csv_row_data.append(asked_data)
            answered_date = question_answer.answered_date.strftime("%Y-%m-%d %H:%M:%S") if question_answer.answered_date else ""
            question_answer_csv_row_data.append(answered_date)
            question_answer_csv_row_data.append(str(question_answer.is_answered_correctly))
            rv.append(question_answer_csv_row_data)

        return rv

    def get_field_names_for_csv(self):
        """ this method gives the fields to export as csv row, in a chosen order """
        rv = super(ExerciseAttempt, self).get_field_names_for_csv()
        rv.extend(['is_validated', 'max_mistakes'])
        return rv
