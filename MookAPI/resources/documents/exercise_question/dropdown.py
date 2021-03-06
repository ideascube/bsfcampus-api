from bson import ObjectId

from MookAPI.core import db
from MookAPI.serialization import JsonSerializer
from . import \
    ExerciseQuestionJsonSerializer,\
    ExerciseQuestion, \
    ExerciseQuestionAnswerJsonSerializer, \
    ExerciseQuestionAnswer


class DropdownExerciseQuestionPropositionJsonSerializer(JsonSerializer):
    pass

class DropdownExerciseQuestionProposition(DropdownExerciseQuestionPropositionJsonSerializer, db.EmbeddedDocument):
    """Stores a proposition to a blank field."""

    ## Object Id
    _id = db.ObjectIdField(default=ObjectId)

    ## Text
    text = db.StringField()

    ## Is correct answer
    is_correct_answer = db.BooleanField(default=False)


class DropdownExerciseQuestionDropdownJsonSerializer(JsonSerializer):
    pass

class DropdownExerciseQuestionDropdown(DropdownExerciseQuestionDropdownJsonSerializer, db.EmbeddedDocument):
    """Stores a list of propositions to a blank field in a text."""

    ## Object Id
    _id = db.ObjectIdField(default=ObjectId)

    ## Text
    propositions = db.ListField(db.EmbeddedDocumentField(DropdownExerciseQuestionProposition))


class DropdownExerciseQuestionJsonSerializer(ExerciseQuestionJsonSerializer):
    pass

class DropdownExerciseQuestion(DropdownExerciseQuestionJsonSerializer, ExerciseQuestion):
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
        return DropdownExerciseQuestionAnswer.init_with_data(data)

    def get_propositions_by_id(self, propositionsId):
        result = []
        for dropdown in self.dropdowns:
            for proposition in dropdown.propositions:
                if proposition._id in propositionsId:
                    result.append(proposition)
        return result


class DropdownExerciseQuestionAnswerJsonSerializer(ExerciseQuestionAnswerJsonSerializer):
    pass

class DropdownExerciseQuestionAnswer(DropdownExerciseQuestionAnswerJsonSerializer, ExerciseQuestionAnswer):
    """Answers given for a dropdown question"""

    ## The list of chosen propositions, identified by their ObjectIds
    given_propositions = db.ListField(db.ObjectIdField())

    @classmethod
    def init_with_data(cls, data):
        obj = cls()
        obj.given_propositions = []
        import re
        for key in data:
            match = re.match(r"dropdown_(\w+)", key)
            if match:
                obj.given_propositions.append(ObjectId(data[key]))
        return obj

    def is_correct(self, question, parameters):
        propositions = question.get_propositions_by_id(self.given_propositions)
        all_question_propositions = []
        for dropdown in question.dropdowns:
            all_question_propositions.extend(dropdown.propositions)
        correct_propositions = filter(lambda proposition: proposition.is_correct_answer, all_question_propositions)
        return set(propositions) == set(correct_propositions)
