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

    def __unicode__(self):
        if self.exercise is not None:
            return self.exercise.title
        return self.id

    def all_syncable_items(self, local_server=None):
        top_level_syncable_document = self.track.top_level_syncable_document()
        if local_server:
            if local_server.syncs_document(top_level_syncable_document):
                return super(TrackValidationAttempt, self).all_syncable_items(local_server=local_server)
        return []

