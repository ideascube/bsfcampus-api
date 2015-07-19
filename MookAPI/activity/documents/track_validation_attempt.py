from exercise_attempt import ExerciseAttemptJsonSerializer, ExerciseAttempt

class TrackValidationAttemptJsonSerializer(ExerciseAttemptJsonSerializer):
    pass

class TrackValidationAttempt(TrackValidationAttemptJsonSerializer, ExerciseAttempt):
    """
    Records any attempt at a track validation test.
    """

    @property
    def track(self):
        return self.exercise.track

    def clean(self):
        super(TrackValidationAttempt, self).clean()
        self.type = "track_validation_attempt"
