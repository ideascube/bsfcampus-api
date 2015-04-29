from bson import ObjectId

from MookAPI import db
from . import ExerciseQuestion, ExerciseQuestionAnswer


class MultipleAnswerMCQExerciseQuestionProposition(db.EmbeddedDocument):
    """Stores a proposition to a multiple-answer MCQ."""

    ## Object Id
    _id = db.ObjectIdField(default=ObjectId)

    ## Text
    text = db.StringField()

    ## Is correct answer
    is_correct_answer = db.BooleanField(default=False)


class MultipleAnswerMCQExerciseQuestion(ExerciseQuestion):
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
        return MultipleAnswerMCQExerciseQuestionAnswer().init_with_data(data)

    def getPropositionsById(self, propositionsId):
        result = [];
        for proposition in self.propositions:
            print(str(proposition._id))
            if proposition._id in propositionsId:
                result.append(proposition)
        return result


class MultipleAnswerMCQExerciseQuestionAnswer(ExerciseQuestionAnswer):
    """Answers given to a multiple-answer MCQ."""

    ## The list of chosen propositions, identified by their ObjectIds
    given_propositions = db.ListField(db.ObjectIdField())

    def init_with_data(self, data):
        self.given_propositions = []
        for proposition in data['propositions']:
            self.given_propositions.append(ObjectId(proposition))
        return self

    def is_correct(self, question, parameters):
        propositions = question.getPropositionsById(self.given_propositions)
        correct_propositions = filter(lambda proposition: proposition.is_correct_answer, question.propositions)
        return set(propositions) == set(correct_propositions)
