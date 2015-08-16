from bson import ObjectId
from random import shuffle

from MookAPI.core import db
from MookAPI.serialization import JsonSerializer
from . import ExerciseQuestionJsonSerializer,\
    ExerciseQuestion, \
    ExerciseQuestionAnswerJsonSerializer, \
    ExerciseQuestionAnswer


class OrderingExerciseQuestionItemJsonSerializer(JsonSerializer):
    pass

class OrderingExerciseQuestionItem(OrderingExerciseQuestionItemJsonSerializer, db.EmbeddedDocument):
    """Stores an item for the overall ordering question."""

    ## Object Id
    _id = db.ObjectIdField(default=ObjectId)

    ## Text
    text = db.StringField()


class OrderingExerciseQuestionOrderingExerciseQuestionItemJsonSerializer(ExerciseQuestionJsonSerializer):
    pass

class OrderingExerciseQuestion(OrderingExerciseQuestionOrderingExerciseQuestionItemJsonSerializer, ExerciseQuestion):
    """A list of items that need to be ordered. May be horizontal or vertical"""

    ## Object Id
    _id = db.ObjectIdField(default=ObjectId)

    ## Propositions
    items = db.ListField(db.EmbeddedDocumentField(OrderingExerciseQuestionItem))

    def without_correct_answer(self):
        son = super(OrderingExerciseQuestion, self).without_correct_answer()
        shuffle(son['items'])
        return son

    def answer_with_data(self, data):
        return OrderingExerciseQuestionAnswer.init_with_data(data)

    def get_items_by_id(self, itemsId):
        result = []
        for itemId in itemsId:
            print(itemId)
            result.append(self.get_item_by_id(itemId))
        return result

    def get_item_by_id(self, itemId):
        for item in self.items:
            if str(item._id) == itemId:
                return item
        return None


class OrderingExerciseQuestionAnswerJsonSerializer(ExerciseQuestionAnswerJsonSerializer):
    pass

class OrderingExerciseQuestionAnswer(OrderingExerciseQuestionAnswerJsonSerializer, ExerciseQuestionAnswer):
    """Ordered items given for this ordering question."""

    ## The given propositions, identified by their ObjectIds
    given_ordered_items = db.ListField(db.ObjectIdField())

    @classmethod
    def init_with_data(cls, data):
        obj = cls()
        obj.given_ordered_items = data['ordered_items']
        return obj

    def is_correct(self, question, parameters):
        ordered_items = question.get_items_by_id(self.given_ordered_items)
        correct_ordered_items = question.items
        return ordered_items == correct_ordered_items
