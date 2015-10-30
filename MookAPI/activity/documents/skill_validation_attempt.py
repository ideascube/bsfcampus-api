import datetime
from bson import ObjectId, DBRef

from MookAPI.core import db
from . import ActivityJsonSerializer, Activity
from exercise_attempt import ExerciseAttemptQuestionAnswer

class SkillValidationAttemptJsonSerializer(ActivityJsonSerializer):

    @staticmethod
    def question_answers_modifier(son, attempt):
        for (index, qa) in enumerate(attempt.question_answers):
            if attempt.skill and not isinstance(attempt.skill, DBRef):
                question = attempt.skill.question(qa.question_id)
                if qa.given_answer is not None:
                    son[index]['question'] = question.with_computed_correct_answer(qa.parameters)
                else:
                    son[index]['question'] = question.without_correct_answer()
                    break

        return son

    __json_additional__ = ['max_mistakes']
    __json_modifiers__ = dict(
        question_answers=question_answers_modifier.__func__
    )

class SkillValidationAttempt(SkillValidationAttemptJsonSerializer, Activity):
    """
    Records any attempt at an exercise.
    """

    ### PROPERTIES

    ## Skill
    skill = db.ReferenceField('Skill')

    @property
    def object(self):
        return self.skill

    ## Question answers
    question_answers = db.ListField(db.EmbeddedDocumentField(ExerciseAttemptQuestionAnswer))

    is_validated = db.BooleanField(default=False)
    """ Is exercise validated """

    end_date = db.DateTimeField()
    """ The date when the attempt is ended """

    @property
    def max_mistakes(self):
        if self.skill and not isinstance(self.skill, DBRef):
            return self.skill.validation_exercise.max_mistakes
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
    def init_with_skill(cls, skill):
        """Initiate an validation attempt for a given skill."""
        obj = cls()
        obj.skill = skill

        questions = skill.random_questions()
        obj.question_answers = map(lambda q: ExerciseAttemptQuestionAnswer.init_with_question(q), questions)

        return obj

    def clean(self):
        super(SkillValidationAttempt, self).clean()
        self.type = "exercise_attempt"

    def __unicode__(self):
        if self.skill is not None:
            return self.skill.title
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

        question = self.skill.question(question_id)
        attempt_question_answer = self.question_answer(question_id)
        question_answer = question.answer_with_data(data)
        attempt_question_answer.given_answer = question_answer
        attempt_question_answer.is_answered_correctly = question_answer.is_correct(
            question,
            attempt_question_answer.parameters
        )
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

    def is_skill_validation_validated(self):
        nb_total_questions = len(self.question_answers)
        answered_questions = filter(lambda a: a.given_answer is not None, self.question_answers)
        return len(answered_questions) >= nb_total_questions

    def is_attempt_completed(self):
        nb_total_questions = len(self.question_answers)
        nb_max_mistakes = self.skill.validation_exercise.max_mistakes
        answered_questions = filter(lambda a: a.given_answer is not None, self.question_answers)
        if len(answered_questions) >= nb_total_questions:
            right_answers = filter(lambda a: a.is_answered_correctly, answered_questions)
            if len(right_answers) >= nb_total_questions - nb_max_mistakes:
                return True

        return False
