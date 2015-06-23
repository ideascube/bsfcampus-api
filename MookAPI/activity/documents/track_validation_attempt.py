__author__ = 'FredFourcade'

from exercise_attempt import ExerciseAttempt


class TrackValidationAttempt(ExerciseAttempt):
    """
    Records any attempt at a track validation test.
    """

    def __unicode__(self):
        if self.exercise is not None:
            return self.exercise.title
        return self.id

