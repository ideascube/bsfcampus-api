from bson import ObjectId

from MookAPI.core import db
from MookAPI.helpers import JsonSerializer
from . import ExerciseQuestionJsonSerializer,\
    ExerciseQuestion, \
    ExerciseQuestionAnswerJsonSerializer, \
    ExerciseQuestionAnswer


class MultipleAnswerMCQExerciseQuestionPropositionJsonSerializer(JsonSerializer):
    pass

class MultipleAnswerMCQExerciseQuestionProposition(MultipleAnswerMCQExerciseQuestionPropositionJsonSerializer, db.EmbeddedDocument):
    """Stores a proposition to a multiple-answer MCQ."""

    ## Object Id
    _id = db.ObjectIdField(default=ObjectId)

    ## Text
    text = db.StringField()

    ## Is correct answer
    is_correct_answer = db.BooleanField(default=False)


class MultipleAnswerMCQExerciseQuestionJsonSerializer(ExerciseQuestionJsonSerializer):
    pass

class MultipleAnswerMCQExerciseQuestion(MultipleAnswerMCQExerciseQuestionJsonSerializer, ExerciseQuestion):
    """Multiple choice question with several possible answers."""

    ## Object Id
    _id = db.ObjectIdField(default=ObjectId)

    ## Propositions
    propositions = db.ListField(db.EmbeddedDocumentField(MultipleAnswerMCQExerciseQuestionProposition))

    def without_correct_answer(self):
        son = super(MultipleAnswerMCQExerciseQuestion, self).without_correct_answer()
        for proposition in son['propositions']:
            proposition.pop('is_correct_answer', None)
        return son

    def answer_with_data(self, data):
        return MultipleAnswerMCQExerciseQuestionAnswer.init_with_data(data)

    def get_propositions_by_id(self, propositions_id):
        result = []
        for proposition in self.propositions:
            print(str(proposition._id))
            if proposition._id in propositions_id:
                result.append(proposition)
        return result


class MultipleAnswerMCQExerciseQuestionAnswerJsonSerializer(ExerciseQuestionAnswerJsonSerializer):
    pass

class MultipleAnswerMCQExerciseQuestionAnswer(MultipleAnswerMCQExerciseQuestionAnswerJsonSerializer, ExerciseQuestionAnswer):
    """Answers given to a multiple-answer MCQ."""

    ## The list of chosen propositions, identified by their ObjectIds
    given_propositions = db.ListField(db.ObjectIdField())

    @classmethod
    def init_with_data(cls, data):
        obj = cls()
        obj.given_propositions = []
        for proposition in data['propositions']:
            obj.given_propositions.append(ObjectId(proposition))
        return obj

    def is_correct(self, question, parameters):
        propositions = question.get_propositions_by_id(self.given_propositions)
        correct_propositions = filter(lambda proposition: proposition.is_correct_answer, question.propositions)
        return set(propositions) == set(correct_propositions)
