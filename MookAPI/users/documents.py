from passlib.hash import bcrypt
import bson

from MookAPI.core import db
from MookAPI.sync import SyncableDocument


class Role(SyncableDocument):
    name = db.StringField(max_length=80, unique=True)

    description = db.StringField()

    def __unicode__(self):
        return self.name


class User(SyncableDocument):

    full_name = db.StringField(unique=False, required=True)

    username = db.StringField(unique=True, required=True)

    email = db.EmailField(unique=False)

    password = db.StringField()

    active = db.BooleanField(default=True)

    accept_cgu = db.BooleanField(required=True, default=False)

    roles = db.ListField(db.ReferenceField(Role))

    exercises_attempts = db.ListField(db.ReferenceField('ExerciseAttempt'), default=[], required=False)

    skill_validation_attempts = db.ListField(db.ReferenceField('SkillValidationAttempt'), default=[], required=False)

    track_validation_attempts = db.ListField(db.ReferenceField('TrackValidationAttempt'), default=[], required=False)

    completed_resources = db.ListField(db.ReferenceField('Resource'), default=[], required=False)

    completed_skills = db.ListField(db.ReferenceField('Skill'), default=[], required=False)

    started_tracks = db.ListField(db.ReferenceField('Track'), default=[], required=False)

    unlocked_track_tests = db.ListField(db.ReferenceField('Track'), default=[], required=False)

    completed_tracks = db.ListField(db.ReferenceField('Track'), default=[], required=False)

    def add_exercise_attempt(self, attempt):
        if attempt not in self.exercises_attempts:
            self.exercises_attempts.append(attempt)

    def add_skill_validation_attempt(self, attempt):
        if attempt not in self.skill_validation_attempts:
            self.skill_validation_attempts.append(attempt)

    def add_track_validation_attempt(self, attempt):
        if attempt not in self.track_validation_attempts:
            self.track_validation_attempts.append(attempt)

    def add_completed_resource(self, resource):
        if resource not in self.completed_resources:
            self.completed_resources.append(resource)
            skill = resource.parent.skill
            skill_progress = skill.user_progress(self)
            if skill not in self.completed_skills and skill_progress['current'] >= skill_progress['max']:
                self.add_completed_skill(skill)

    def add_completed_skill(self, skill):
        if skill not in self.completed_skills:
            self.completed_skills.append(skill)
            track = skill.track
            track_progress = track.user_progress(self)
            if track not in self.unlocked_track_tests and track_progress['current'] >= track_progress['max']:
                self.unlock_track_validation_test(track)

    def add_started_track(self, track):
        if track not in self.started_tracks:
            self.started_tracks.append(track)

    def unlock_track_validation_test(self, track):
        if track not in self.unlocked_track_tests:
            self.unlocked_track_tests.append(track)

    def add_completed_track(self, track):
        if track not in self.completed_tracks:
            self.completed_tracks.append(track)

    @classmethod
    def get_unique_object_or_404(cls, token):
        """Get the only hierarchy level matching argument 'token', where 'token' can be the id or the slug."""

        try:
            bson.ObjectId(token)
        except bson.errors.InvalidId:
            return cls.objects.get_or_404(username=token)
        else:
            return cls.objects.get_or_404(id=token)

    @staticmethod
    def hash_pass(password):
        """
        Return the md5 hash of the password+salt
        """
        return bcrypt.encrypt(password)

    def verify_pass(self, password):
        return bcrypt.verify(password, self.password)

    def __unicode__(self):
        return self.username or self.email or self.id
