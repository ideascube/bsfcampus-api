from bson import ObjectId

from MookAPI.core import db
from MookAPI.helpers import JsonSerializer
from . import ExerciseQuestionJsonSerializer,\
    ExerciseQuestion, \
    ExerciseQuestionAnswerJsonSerializer, \
    ExerciseQuestionAnswer


class RightOrWrongExerciseQuestionPropositionJsonSerializer(JsonSerializer):
    pass

class RightOrWrongExerciseQuestionProposition(RightOrWrongExerciseQuestionPropositionJsonSerializer, db.EmbeddedDocument):
    """Stores a proposition to a right or wrong question."""

    ## Object Id
    _id = db.ObjectIdField(default=ObjectId)

    ## Text
    text = db.StringField()

    ## Is correct answer
    is_correct_answer = db.BooleanField(default=False)


class RightOrWrongExerciseQuestionJsonSerializer(ExerciseQuestionJsonSerializer):
    pass

class RightOrWrongExerciseQuestion(RightOrWrongExerciseQuestionJsonSerializer, ExerciseQuestion):
    """Question with a right or wrong answer"""

    ## Object Id
    _id = db.ObjectIdField(default=ObjectId)

    ## Propositions
    propositions = db.ListField(db.EmbeddedDocumentField(RightOrWrongExerciseQuestionProposition))

    def without_correct_answer(self):
        son = super(RightOrWrongExerciseQuestion, self).without_correct_answer()
        for proposition in son['propositions']:
            proposition.pop('is_correct_answer', None)
        return son

    def answer_with_data(self, data):
        return RightOrWrongExerciseQuestionAnswer.init_with_data(data)

    def get_proposition_by_id(self, propositionId):
        result = None;
        for proposition in self.propositions:
            if proposition._id == propositionId:
                result = proposition
        return result


class RightOrWrongExerciseQuestionAnswerJsonSerializer(ExerciseQuestionAnswerJsonSerializer):
    pass

class RightOrWrongExerciseQuestionAnswer(RightOrWrongExerciseQuestionAnswerJsonSerializer, ExerciseQuestionAnswer):
    """Answer given to a right or wrong question."""

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
