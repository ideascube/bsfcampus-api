import flask
from MookAPI import db
from flask.ext.security import Security, UserMixin, RoleMixin
from MookAPI.resources.documents import Resource
from MookAPI.hierarchy.documents import Track, Skill
from MookAPI.activity.documents.exercise_attempt import ExerciseAttempt


class Role(db.Document, RoleMixin):
    name = db.StringField(max_length=80, unique=True)

    description = db.StringField()

    def __unicode__(self):
        return self.name


class User(db.Document, UserMixin):
    first_name = db.StringField()

    last_name = db.StringField()

    username = db.StringField()  # To make this unique we first need to update the registration form to include the field.

    email = db.EmailField(unique=True, required=True)

    password = db.StringField()

    active = db.BooleanField(default=True)

    accept_cgu = db.BooleanField(default=False)

    roles = db.ListField(db.ReferenceField(Role), default=[])

    exercises_attempts = db.ListField(db.ReferenceField(ExerciseAttempt), default=[])

    completed_resources = db.ListField(db.ReferenceField(Resource), default=[])

    completed_skills = db.ListField(db.ReferenceField(Skill), default=[])

    started_tracks = db.ListField(db.ReferenceField(Track), default=[])

    unlocked_track_tests = db.ListField(db.ReferenceField(Track), default=[])

    completed_tracks = db.ListField(db.ReferenceField(Track), default=[])

    def __unicode__(self):
        if self.email is None and self.username is not None:
            return self.username

        return self.email

    def add_exercise_attempt(self, attempt):
        if attempt not in self.exercises_attempts:
            self.exercises_attempts.append(attempt)
            self.save()

    def add_completed_resource(self, resource):
        if resource not in self.completed_resources:
            self.completed_resources.append(resource)
            skill = resource.lesson.skill
            skill_progress = skill.progress
            if skill not in self.completed_skills and skill_progress['current'] >= skill_progress['max']:
                self.add_completed_skill(skill)
            self.save()

    def add_completed_skill(self, skill):
        if skill not in self.completed_skills:
            self.completed_skills.append(skill)
            track = skill.track
            track_progress = track.progress
            if track not in self.unlocked_track_tests and track_progress['current'] >= track_progress['max']:
                self.unlock_track_validation_test(track)
            self.save()

    def add_started_track(self, track):
        if track not in self.started_tracks:
            self.started_tracks.append(track)
            self.save()

    def unlock_track_validation_test(self, track):
        if track not in self.unlocked_track_tests:
            self.unlocked_track_tests.append(track)
            self.save()

    def add_completed_track(self, track):
        if track not in self.completed_tracks:
            self.completed_tracks.append(track)
            self.save()
