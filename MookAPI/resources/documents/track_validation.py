__author__ = 'FredFourcade'

from exercise import ExerciseResource
from MookAPI import db

class TrackValidationResource(ExerciseResource):
    """An track validation test with a list of questions."""

    parent = db.ReferenceField('Track')
    """The parent Hierarchy object (here, it is a Track)."""