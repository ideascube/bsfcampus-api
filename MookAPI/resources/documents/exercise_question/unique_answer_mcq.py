from bson import ObjectId

from MookAPI import db
from . import ExerciseQuestion, ExerciseQuestionAnswer
from MookAPI.local_servers.documents import SyncableDocument, SyncableEmbeddedDocument


class UniqueAnswerMCQExerciseQuestionProposition(SyncableEmbeddedDocument):
    """Stores a proposition to a unique-answer MCQ."""

    ## Object Id
    _id = db.ObjectIdField(default=ObjectId)

    ## Text
    text = db.StringField()

    ## Is correct answer
    is_correct_answer = db.BooleanField(default=False)


class UniqueAnswerMCQExerciseQuestion(ExerciseQuestion):
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
        return UniqueAnswerMCQExerciseQuestionAnswer().init_with_data(data)

    def propositionById(self, propositionId):
        result = None;
        for proposition in self.propositions:
            if proposition._id == propositionId:
                result = proposition
        return result


class UniqueAnswerMCQExerciseQuestionAnswer(ExerciseQuestionAnswer):
    """Answer given to a unique-answer MCQ."""

    ## The chosen propositions, identified by its ObjectId
    given_proposition = db.ObjectIdField()

    def init_with_data(self, data):
        self.given_proposition = data['proposition']
        print(self.given_proposition)
        return self

    def is_correct(self, question, parameters):
        proposition = question.propositionById(ObjectId(self.given_proposition))
        if (proposition != None):
            return proposition.is_correct_answer
        return False
