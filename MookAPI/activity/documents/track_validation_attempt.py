from bson import DBRef

from exercise_attempt import ExerciseAttemptJsonSerializer, ExerciseAttempt

class TrackValidationAttemptJsonSerializer(ExerciseAttemptJsonSerializer):
    pass

class TrackValidationAttempt(TrackValidationAttemptJsonSerializer, ExerciseAttempt):
    """
    Records any attempt at a track validation test.
    """

    @property
    def track(self):
        if self.exercise and not isinstance(self.exercise, DBRef):
            return self.exercise.track
        return None

    def clean(self):
        super(TrackValidationAttempt, self).clean()
        self.type = "track_validation_attempt"
