from bson import ObjectId

from MookAPI.core import db
from MookAPI.helpers import JsonSerializer
from . import ExerciseQuestionJsonSerializer,\
    ExerciseQuestion, \
    ExerciseQuestionAnswerJsonSerializer, \
    ExerciseQuestionAnswer


class UniqueAnswerMCQExerciseQuestionPropositionJsonSerializer(JsonSerializer):
    pass

class UniqueAnswerMCQExerciseQuestionProposition(UniqueAnswerMCQExerciseQuestionPropositionJsonSerializer, db.EmbeddedDocument):
    """Stores a proposition to a unique-answer MCQ."""

    ## Object Id
    _id = db.ObjectIdField(default=ObjectId)

    ## Text
    text = db.StringField()

    ## Is correct answer
    is_correct_answer = db.BooleanField(default=False)


class UniqueAnswerMCQExerciseQuestionJsonSerializer(ExerciseQuestionJsonSerializer):
    pass

class UniqueAnswerMCQExerciseQuestion(UniqueAnswerMCQExerciseQuestionJsonSerializer, ExerciseQuestion):
    """Multiple choice question with one possible answer only."""

    ## Object Id
    _id = db.ObjectIdField(default=ObjectId)

    ## Propositions
    propositions = db.ListField(db.EmbeddedDocumentField(UniqueAnswerMCQExerciseQuestionProposition))

    def without_correct_answer(self):
        son = super(UniqueAnswerMCQExerciseQuestion, self).without_correct_answer()
        for proposition in son['propositions']:
            proposition.pop('is_correct_answer', None)
        return son

    def answer_with_data(self, data):
        return UniqueAnswerMCQExerciseQuestionAnswer.init_with_data(data)

    def get_proposition_by_id(self, propositionId):
        result = None
        for proposition in self.propositions:
            if proposition._id == propositionId:
                result = proposition
        return result


class UniqueAnswerMCQExerciseQuestionAnswerJsonSerializer(ExerciseQuestionAnswerJsonSerializer):
    pass

class UniqueAnswerMCQExerciseQuestionAnswer(UniqueAnswerMCQExerciseQuestionAnswerJsonSerializer, ExerciseQuestionAnswer):
    """Answer given to a unique-answer MCQ."""

    ## The chosen propositions, identified by its ObjectId
    given_proposition = db.ObjectIdField()

    @classmethod
    def init_with_data(cls, data):
        obj = cls()
        obj.given_proposition = data['proposition']
        return obj

    def is_correct(self, question, parameters):
        proposition = question.get_proposition_by_id(ObjectId(self.given_proposition))
        if (proposition != None):
            return proposition.is_correct_answer
        return False
