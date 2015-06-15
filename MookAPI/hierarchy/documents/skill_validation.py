import MookAPI.mongo_coder as mc
from MookAPI import db

class SkillValidationExercise(mc.MongoCoderEmbeddedDocument):

    number_of_questions = db.IntField()
    """The number of questions to ask from this exercise."""

    max_mistakes = db.IntField()
    """The number of mistakes authorized before failing the exercise."""
