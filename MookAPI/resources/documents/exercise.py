from . import *
from exercise_question.unique_answer_mcq import UniqueAnswerMCQExerciseQuestion
from exercise_question.multiple_answer_mcq import MultipleAnswerMCQExerciseQuestion
from exercise_question.right_or_wrong import RightOrWrongExerciseQuestion
from exercise_question.dropdown import DropdownExerciseQuestion
from exercise_question.ordering import OrderingExerciseQuestion
from exercise_question.categorize import CategorizeExerciseQuestion
from random import shuffle
from bson import ObjectId
import exceptions


class ExerciseResourceContent(ResourceContent):
    """An exercise with a list of questions."""

    ## Embedded list of questions of type Unique Answer MCQ
    unique_answer_mcq_questions = db.ListField(db.EmbeddedDocumentField(UniqueAnswerMCQExerciseQuestion))

    ## Embedded list of questions of type Multiple Answer MCQ
    multiple_answer_mcq_questions = db.ListField(db.EmbeddedDocumentField(MultipleAnswerMCQExerciseQuestion))

    ## Embedded list of questions of type Right or Wrong
    right_or_wrong_questions = db.ListField(db.EmbeddedDocumentField(RightOrWrongExerciseQuestion))

    ## Embedded list of questions of type Dropdown
    dropdown_questions = db.ListField(db.EmbeddedDocumentField(DropdownExerciseQuestion))

    ## Embedded list of questions of type Ordering
    ordering_questions = db.ListField(db.EmbeddedDocumentField(OrderingExerciseQuestion))

    ## Embedded list of questions of type Categorize
    categorize_questions = db.ListField(db.EmbeddedDocumentField(CategorizeExerciseQuestion))

    def questions(self):
        questions = []
        questions.extend(self.unique_answer_mcq_questions)
        questions.extend(self.multiple_answer_mcq_questions)
        questions.extend(self.right_or_wrong_questions)
        questions.extend(self.dropdown_questions)
        questions.extend(self.ordering_questions)
        questions.extend(self.categorize_questions)
        return questions


class ExerciseResource(Resource):
    resource_content = db.EmbeddedDocumentField(ExerciseResourceContent)

    number_of_questions = db.IntField();

    max_mistakes = db.IntField();

    fail_linked_resource = db.ReferenceField(Resource)

    def questions(self):
        return self.resource_content.questions()

    def question(self, question_id):
        print("ExerciseResource.question " + str(question_id))
        oid = ObjectId(question_id)
        for question in self.questions():
            print("question._id " + str(question._id))
            if question._id == oid:
                return question
        raise exceptions.KeyError("Question not found.")

    def random_questions(self, number):
        all_questions = self.questions()
        shuffle(all_questions)
        return all_questions[:number]
