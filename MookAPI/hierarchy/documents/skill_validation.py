import random

import MookAPI.mongo_coder as mc
from MookAPI import db

class SkillValidationExercise(mc.MongoCoderEmbeddedDocument):

    number_of_questions = db.IntField()
    """The number of questions to ask from this exercise."""

    max_mistakes = db.IntField()
    """The number of mistakes authorized before failing the exercise."""

    def random_questions(self, skill, number=None):
        """
        A list of random questions picked from the skill's children exercises.
        If `number` is not specified, it will be set to the skillValidationExercise's `number_of_questions` property.
        The list will contain `number` questions, or all questions if there are not enough questions in the exercise.
        """

        if not number:
            number = self.number_of_questions

        all_questions = skill.questions
        random.shuffle(all_questions)
        return all_questions[:number]
