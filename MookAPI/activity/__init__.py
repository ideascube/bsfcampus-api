from MookAPI.core import Service
from .documents import Activity
from .documents.exercise_attempt import ExerciseAttempt
from .documents.skill_validation_attempt import SkillValidationAttempt
from .documents.track_validation_attempt import TrackValidationAttempt


class ActivitiesService(Service):
    __model__ = Activity

class ExerciseAttemptsService(Service):
    __model__ = ExerciseAttempt

class SkillValidationAttemptsService(Service):
    __model__ = SkillValidationAttempt

class TrackValidationAttemptsService(Service):
    __model__ = TrackValidationAttempt
