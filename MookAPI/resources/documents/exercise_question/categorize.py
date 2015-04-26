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
            all_items.extend(category['items'])
        shuffle(all_items)
        son['items'] = all_items
        son.pop('categories')
        return son

    def answer_with_data(self, data):
        return CategorizeExerciseQuestionAnswer().init_with_data(data)

    def getItemsById(self, categoryIndex, itemsId):
        result = [];
        category = self.categories[categoryIndex]
        for item in category.items:
            if item._id in itemsId:
                result.append(item)
        return result


class CategorizeExerciseQuestionAnswer(ExerciseQuestionAnswer):
    """categorized items given for this Categorize question."""

    ## The categorized items, identified by their ObjectIds, in the requested categories
    given_categorized_items = db.ListField(db.ListField(db.ObjectIdField()))

    def init_with_data(self, data):
        self.given_categorized_items = []
        for given_category in data.getlist('given_categorized_items[]'):
            category = []
            for given_item in given_category:
                category.append(ObjectId(given_item))
            self.given_categorized_items.append(category)
        return self

    def is_correct(self, question, parameters):
        answer_categories = self.given_categorized_items
        result = True
        for i in range(0, len(given_categorized_items)):
            category_items = question.getItemsInCategoryById(i, given_categorized_items[i])
            if set(category_items) != set(question.categories[i].items):
                result = False
                break
        return result
