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
        # TODO: check if skill is completed
        if resource not in self.completed_resources:
            self.completed_resources.append(resource)
            self.save()

    def add_completed_skill(self, skill):
        # TODO: check if track is completed
        if skill not in self.completed_skills:
            self.completed_skills.append(skill)
            self.save()

    def add_completed_track(self, track):
        if track not in self.completed_tracks:
            self.completed_tracks.append(track)
            self.save()
