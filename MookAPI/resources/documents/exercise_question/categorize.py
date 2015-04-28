from random import shuffle

from bson import ObjectId

from MookAPI import db
from . import ExerciseQuestion, ExerciseQuestionAnswer


class CategorizeExerciseQuestionItem(db.EmbeddedDocument):
    """Stores an item that belongs to one category."""

    ## Object Id
    _id = db.ObjectIdField(default=ObjectId)

    ## Text
    text = db.StringField()


class CategorizeExerciseQuestionCategory(db.EmbeddedDocument):
    """Stores a category for the categorize question."""

    ## Object Id
    _id = db.ObjectIdField(default=ObjectId)

    ## Text
    title = db.StringField()

    ## items that belong to this category
    items = db.ListField(db.EmbeddedDocumentField(CategorizeExerciseQuestionItem))


class CategorizeExerciseQuestion(ExerciseQuestion):
    """A list of items that need to be categorized."""

    ## Object Id
    _id = db.ObjectIdField(default=ObjectId)

    ## categories
    categories = db.ListField(db.EmbeddedDocumentField(CategorizeExerciseQuestionCategory))

    def without_correct_answer(self):
        son = super(CategorizeExerciseQuestion, self).without_correct_answer()
        all_items = []
        for category in son['categories']:
            print(category)
            all_items.extend(category.pop('items'))
        shuffle(all_items)
        son['items'] = all_items
        return son

    def answer_with_data(self, data):
        return CategorizeExerciseQuestionAnswer().init_with_data(data)

    def get_category_by_id(self, category_id):
        for category in self.categories:
            if category._id == category_id:
                return category

    def get_items_in_category_by_id(self, category_id, items_id):
        result = []
        category = self.get_category_by_id(category_id)
        for item in category.items:
            if item._id in items_id:
                result.append(item)
        return result


class CategorizeExerciseQuestionAnswer(ExerciseQuestionAnswer):
    """categorized items given for this Categorize question."""

    ## The categories sent by the client, identified by their ObjectIds.
    given_categories = db.ListField(db.ObjectIdField())

    ## The categorized items, identified by their ObjectIds, in the requested categories.
    ## The first level order is the same as the given_categories
    given_categorized_items = db.ListField(db.ListField(db.ObjectIdField()))

    def init_with_data(self, data):
        self.given_categories = []
        self.given_categorized_items = []
        for given_category in data['given_categorized_items']:
            self.given_categories.append(ObjectId(given_category['id']))
            category = []
            for given_item in given_category['items']:
                category.append(ObjectId(given_item))
            self.given_categorized_items.append(category)
        return self

    def is_correct(self, question, parameters):
        answer_categories_items = self.given_categorized_items
        result = True
        for i in range(0, len(answer_categories_items)):
            category_items = question.get_items_in_category_by_id(self.given_categories[i],
                                                                  self.given_categorized_items[i])
            correct_category = question.get_category_by_id(self.given_categories[i])
            if set(category_items) != set(correct_category.items):
                result = False
                break
        return result
