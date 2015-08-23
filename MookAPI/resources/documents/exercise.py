import bson
import exceptions
import random
import datetime
import math

from . import ResourceContentJsonSerializer, \
    ResourceContent, \
    Resource, \
    ResourceJsonSerializer
from MookAPI.core import db

from exercise_question.unique_answer_mcq import UniqueAnswerMCQExerciseQuestion
from exercise_question.multiple_answer_mcq import MultipleAnswerMCQExerciseQuestion
from exercise_question.right_or_wrong import RightOrWrongExerciseQuestion
from exercise_question.dropdown import DropdownExerciseQuestion
from exercise_question.ordering import OrderingExerciseQuestion
from exercise_question.categorize import CategorizeExerciseQuestion


class ExerciseResourceContentJsonSerializer(ResourceContentJsonSerializer):
    pass


class ExerciseResourceContent(ExerciseResourceContentJsonSerializer, ResourceContent):
    unique_answer_mcq_questions = db.ListField(db.EmbeddedDocumentField(UniqueAnswerMCQExerciseQuestion))
    """A (possibly empty) list of unique-answer multiple-choice questions (`UniqueAnswerMCQExerciseQuestion`)."""

    multiple_answer_mcq_questions = db.ListField(db.EmbeddedDocumentField(MultipleAnswerMCQExerciseQuestion))
    """A (possibly empty) list of multiple-answer multiple-choice questions (`MultipleAnswerMCQExerciseQuestion`)."""

    right_or_wrong_questions = db.ListField(db.EmbeddedDocumentField(RightOrWrongExerciseQuestion))
    """A (possibly empty) list of multiple-answer multiple-choice questions (`RightOrWrongExerciseQuestion`)."""

    dropdown_questions = db.ListField(db.EmbeddedDocumentField(DropdownExerciseQuestion))
    """A (possibly empty) list of dropdown questions (`DropdownExerciseQuestion`)."""

    ordering_questions = db.ListField(db.EmbeddedDocumentField(OrderingExerciseQuestion))
    """A (possibly empty) list of ordering questions (`OrderingExerciseQuestion`)."""

    categorize_questions = db.ListField(db.EmbeddedDocumentField(CategorizeExerciseQuestion))
    """A (possibly empty) list of categorizing questions (`CategorizeExerciseQuestion`)."""

    @property
    def questions(self):
        """A list of all questions, whatever their type."""

        questions = []
        questions.extend(self.unique_answer_mcq_questions)
        questions.extend(self.multiple_answer_mcq_questions)
        questions.extend(self.right_or_wrong_questions)
        questions.extend(self.dropdown_questions)
        questions.extend(self.ordering_questions)
        questions.extend(self.categorize_questions)

        return questions

    def question(self, question_id):
        """A getter for a question with a known `_id`."""

        oid = bson.ObjectId(question_id)
        for question in self.questions:
            if question._id == oid:
                return question

        raise exceptions.KeyError("Question not found.")

    def random_questions(self, number=None):
        """
        A list of random questions.
        If `number` is not specified, it will be set to the exercise's `number_of_questions` property.
        The list will contain `number` questions, or all questions if there are not enough questions in the exercise.
        """

        if not number:
            number = self.number_of_questions or len(self.questions)

        all_questions = self.questions
        random.shuffle(all_questions)
        return all_questions[:number]

    number_of_questions = db.IntField()
    """The number of questions to ask from this exercise."""

    max_mistakes = db.IntField()
    """The number of mistakes authorized before failing the exercise."""

    fail_linked_resource = db.ReferenceField(Resource)
    """A resource to look again when failing the exercise."""

    def clean(self):
        super(ExerciseResourceContent, self).clean()
        # FIXME This should be done in validate and raise an error. Do that when MongoEngine is fixed.
        if self.fail_linked_resource:
            if self.fail_linked_resource.track != self._instance.track:
                self.fail_linked_resource = None


class ExerciseResourceJsonSerializer(ResourceJsonSerializer):
    pass


class ExerciseResource(ExerciseResourceJsonSerializer, Resource):
    """An exercise with a list of questions."""

    resource_content = db.EmbeddedDocumentField(ExerciseResourceContent)

    def _add_instance(self, obj):
        """This is a hack to provide the ``_instance`` property to the shorthand question-getters."""

        def _add_instance_single_object(obj):
            obj._instance = self
            return obj

        if isinstance(obj, list):
            return map(_add_instance_single_object, obj)
        else:
            return _add_instance_single_object(obj)

    @property
    def questions(self):
        """A shorthand getter for the list of questions in the resource content."""

        questions = self.resource_content.questions
        return self._add_instance(questions)

    def question(self, question_id):
        """A shorthand getter for a question with a known `_id`."""

        question = self.resource_content.question(question_id)
        return self._add_instance(question)

    def random_questions(self, number=None):
        """
        A shorthand getter for a list of random questions.
        See the documentation of `ExerciseResourceContent.random_questions`.
        """

        questions = self.resource_content.random_questions(number)
        return self._add_instance(questions)

    def all_syncable_items(self, local_server=None):
        items = []
        if self.resource_content.fail_linked_resource:
            items.append(self.resource_content.fail_linked_resource)
        items.extend(super(ExerciseResource, self).all_syncable_items(local_server=local_server))
        return items

    def user_analytics(self, user):
        rv = super(ExerciseResource, self).user_analytics(user)

        from MookAPI.services import exercise_attempts
        exercise_attempts = exercise_attempts.find(user=user, exercise=self).order_by('-date')
        rv['last_attempts_scores'] = map(
            lambda a: {"date": a.date, "nb_questions": a.nb_questions, "score": a.nb_right_answers},
            exercise_attempts[:5]
        )

        nb_finished_attempts = 0
        total_duration = datetime.timedelta(0)
        for attempt in exercise_attempts:
            if attempt.duration:
                nb_finished_attempts += 1
                total_duration += attempt.duration
        if nb_finished_attempts > 0:
            rv['average_time_on_exercise'] = math.floor((total_duration / nb_finished_attempts).total_seconds())
        else:
            rv['average_time_on_exercise'] = 0

        rv['nb_attempts'] = exercise_attempts.count()

        return rv
