from bson import ObjectId

from MookAPI.core import db
from . import ActivityJsonSerializer, Activity
from exercise_attempt import ExerciseAttemptQuestionAnswer

class SkillValidationAttemptJsonSerializer(ActivityJsonSerializer):

    @staticmethod
    def question_answers_modifier(son, attempt):
        for (index, qa) in enumerate(attempt.question_answers):
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

    ## Question answers
    question_answers = db.ListField(db.EmbeddedDocumentField(ExerciseAttemptQuestionAnswer))

    @property
    def max_mistakes(self):
        return self.skill.validation_exercise.max_mistakes

    ### METHODS

    @classmethod
    def init_with_skill(cls, skill):
        """Initiate an validation attempt for a given skill."""
        obj = cls()
        obj.skill = skill

        questions = skill.random_questions()
        obj.question_answers = map(lambda q: ExerciseAttemptQuestionAnswer.init_with_question(q), questions)

        return obj

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

    def is_skill_validation_completed(self):
        nb_total_questions = self.skill.validation_exercise.number_of_questions
        nb_max_mistakes = self.skill.validation_exercise.max_mistakes
        answered_questions = filter(lambda a: a.given_answer is not None, self.question_answers)
        if len(answered_questions) >= nb_total_questions:
            right_answers = filter(lambda a: a.is_answered_correctly, answered_questions)
            if len(right_answers) >= nb_total_questions - nb_max_mistakes:
                return True

        return False

