from bson import ObjectId

from MookAPI import db
from . import ExerciseQuestion, ExerciseQuestionAnswer
from MookAPI.local_servers.documents import SyncableDocument, SyncableEmbeddedDocument


class DropdownExerciseQuestionProposition(SyncableEmbeddedDocument):
    """Stores a proposition to a blank field."""

    ## Object Id
    _id = db.ObjectIdField(default=ObjectId)

    ## Text
    text = db.StringField()

    ## Is correct answer
    is_correct_answer = db.BooleanField(default=False)


class DropdownExerciseQuestionDropdown(SyncableEmbeddedDocument):
    """Stores a list of propositions to a blank field in a text."""

    ## Object Id
    _id = db.ObjectIdField(default=ObjectId)

    ## Text
    propositions = db.ListField(db.EmbeddedDocumentField(DropdownExerciseQuestionProposition))


class DropdownExerciseQuestion(ExerciseQuestion):
    """question where blanks need to be filled with word chosen from a dropdown list."""

    ## Object Id
    _id = db.ObjectIdField(default=ObjectId)

    ## the whole text, where blanks are tagged with [%N%] where N if Nth blank of the text
    text = db.StringField()

    ## Propositions
    dropdowns = db.ListField(db.EmbeddedDocumentField(DropdownExerciseQuestionDropdown))

    def without_correct_answer(self):
        son = super(DropdownExerciseQuestion, self).without_correct_answer()
        for dropdown in son['dropdowns']:
            for proposition in dropdown['propositions']:
                proposition.pop('is_correct_answer', None)
        return son

    def answer_with_data(self, data):
        return DropdownExerciseQuestionAnswer().init_with_data(data)

    def getPropositionsById(self, propositionsId):
        result = [];
        for dropdown in self.dropdowns:
            for proposition in dropdown.propositions:
                if proposition._id in propositionsId:
                    result.append(proposition)
        return result


class DropdownExerciseQuestionAnswer(ExerciseQuestionAnswer):
    """Answers given for a dropdown question"""

    ## The list of chosen propositions, identified by their ObjectIds
    given_propositions = db.ListField(db.ObjectIdField())

    def init_with_data(self, data):
        self.given_propositions = []
        for dropdown in data['dropdowns']:
            self.given_propositions.append(ObjectId(dropdown))
        return self

    def is_correct(self, question, parameters):
        propositions = question.getPropositionsById(self.given_propositions)
        all_question_propositions = []
        for dropdown in question.dropdowns:
            all_question_propositions.extend(dropdown.propositions)
        correct_propositions = filter(lambda proposition: proposition.is_correct_answer, all_question_propositions)
        return set(propositions) == set(correct_propositions)
