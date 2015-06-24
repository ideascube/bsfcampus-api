import flask
import bson
from MookAPI import db, app
import MookAPI.mongo_coder as mc
from flask.ext.security import Security, UserMixin, RoleMixin
from MookAPI.resources.documents import Resource
from MookAPI.hierarchy.documents import track, skill
from MookAPI.activity.documents.exercise_attempt import ExerciseAttempt
from MookAPI.activity.documents.skill_validation_attempt import SkillValidationAttempt
from MookAPI.activity.documents.track_validation_attempt import TrackValidationAttempt


class Role(db.Document, RoleMixin):
    name = db.StringField(max_length=80, unique=True)

    description = db.StringField()

    def __unicode__(self):
        return self.name


class User(mc.SyncableDocument, UserMixin):
    full_name = db.StringField()

    username = db.StringField()  # To make this unique we first need to update the registration form to include the field.

    email = db.EmailField(unique=True, required=True)

    password = db.StringField()

    active = db.BooleanField(default=True)

    accept_cgu = db.BooleanField(default=False)

    roles = db.ListField(db.ReferenceField(Role), default=[])

    exercises_attempts = db.ListField(db.ReferenceField(ExerciseAttempt), default=[], required=False)

    skill_validation_attempts = db.ListField(db.ReferenceField(SkillValidationAttempt), default=[], required=False)

    track_validation_attempts = db.ListField(db.ReferenceField(TrackValidationAttempt), default=[], required=False)

    completed_resources = db.ListField(db.ReferenceField(Resource), default=[], required=False)

    completed_skills = db.ListField(db.ReferenceField(skill.Skill), default=[], required=False)

    started_tracks = db.ListField(db.ReferenceField(track.Track), default=[], required=False)

    unlocked_track_tests = db.ListField(db.ReferenceField(track.Track), default=[], required=False)

    completed_tracks = db.ListField(db.ReferenceField(track.Track), default=[], required=False)

    def __unicode__(self):
        if self.email is None and self.username is not None:
            return self.username

        return self.email

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
            skill_progress = skill.progress
            if skill not in self.completed_skills and skill_progress['current'] >= skill_progress['max']:
                self.add_completed_skill(skill)

    def add_completed_skill(self, skill):
        if skill not in self.completed_skills:
            self.completed_skills.append(skill)
            track = skill.track
            track_progress = track.progress
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

    @staticmethod
    def hash_pass(password):
        """
        Return the md5 hash of the password+salt
        """
        #  FIXME: the hashing is removed until we change the user authentication process
        # salted_password = password + app.secret_key
        # return sha256_crypt.encrypt(salted_password)
        return password
