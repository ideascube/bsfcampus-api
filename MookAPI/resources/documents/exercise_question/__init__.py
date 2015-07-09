import exceptions
import bson

from flask import url_for

from MookAPI.core import db
from MookAPI.helpers import JsonSerializer


class ExerciseQuestionJsonSerializer(JsonSerializer):
    pass

class ExerciseQuestion(ExerciseQuestionJsonSerializer, db.EmbeddedDocument):
    """
    Generic collection, every question type will inherit from this.
    Subclasses should override method "without_correct_answer" in order to define the version sent to clients.
    Subclasses of questions depending on presentation parameters should also override
    method "with_computed_correct_answer".
    """

    meta = {
        'allow_inheritance': True,
        'abstract': True
    }

    @property
    def id(self):
        return self._id

    ## Object Id
    _id = db.ObjectIdField(default=bson.ObjectId)

    ## Question text
    question_heading = db.StringField()

    ## Question image
    question_image = db.ImageField()

    @property
    def question_image_url(self):
        if not self.question_image:
            return None

        if not hasattr(self, '_instance'):
            return None

        return url_for(
            "resources.get_exercise_question_image",
            resource_id=str(self._instance._instance.id),
            question_id=str(self._id),
            filename=self.question_image.filename,
            _external=True
        )
    

    ## Answer feedback (explanation of the right answer)
    answer_feedback = db.StringField()

    def without_correct_answer(self):
        son = self.to_json()
        son.pop('answer_feedback', None)
        return son

    def with_computed_correct_answer(self, parameters):
        son = self.to_json()
        return son

    def answer_with_data(self, data):
        return ExerciseQuestionAnswer.init_with_data(data)


class ExerciseQuestionAnswerJsonSerializer(JsonSerializer):
    pass

class ExerciseQuestionAnswer(ExerciseQuestionAnswerJsonSerializer, db.EmbeddedDocument):
    """
    Generic collection to save answers given to a question.
    Subclasses should define their own properties to store the given answer.
    They must also override method "is_correct" in order to determine whether the given answer is correct.
    """

    meta = {
        'allow_inheritance': True,
        'abstract': True
    }

    ### PROPERTIES

    ## There is no property common to all types.

    ### METHODS

    @classmethod
    def init_with_data(cls, data):
        raise exceptions.NotImplementedError("This question type has no initializer.")

    ## This method needs to be overridden for each question type.
    def is_correct(self, question, parameters):
        """
        Whether the answer is correct.
        Pass the question itself and the parameters, if any.
        """

        raise exceptions.NotImplementedError("This question type has no correction method.")


__all__ = [
    'ExerciseQuestion',
    'ExerciseQuestionAnswer',
    'categorize',
    'dropdown',
    'multiple_answer_mcq',
    'ordering',
    'right_or_wrong',
    'unique_answer_mcq',
]
