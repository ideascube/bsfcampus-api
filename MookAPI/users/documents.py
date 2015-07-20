from passlib.hash import bcrypt
import bson

from flask import url_for

from MookAPI.core import db
from MookAPI.serialization import JsonSerializer
from MookAPI.sync import SyncableDocumentJsonSerializer, SyncableDocument

class RoleJsonSerializer(SyncableDocumentJsonSerializer):
    pass

class Role(RoleJsonSerializer, SyncableDocument):
    name = db.StringField(max_length=80, unique=True)

    description = db.StringField()

    def __unicode__(self):
        return self.name

class UserJsonSerializer(SyncableDocumentJsonSerializer):
    pass

class User(UserJsonSerializer, SyncableDocument):

    full_name = db.StringField(unique=False, required=True)

    username = db.StringField(unique=True, required=True)

    email = db.EmailField(unique=False)

    password = db.StringField()

    active = db.BooleanField(default=True)

    accept_cgu = db.BooleanField(required=True, default=False)

    roles = db.ListField(db.ReferenceField(Role))

    tutors = db.ListField(db.ReferenceField('self'))

    tutored_students = db.ListField(db.ReferenceField('self'))

    awaiting_tutor_requests = db.ListField(db.ReferenceField('self'))

    awaiting_student_requests = db.ListField(db.ReferenceField('self'))

    def add_completed_resource(self, resource):
        from MookAPI.services import completed_resources
        if completed_resources.find(user=self, resource=resource).count() == 0:
            completed_resources.create(user=self, resource=resource)
            skill = resource.parent.skill
            skill_progress = skill.user_progress(self)
            from MookAPI.services import completed_skills
            if completed_skills.find(user=self, skill=skill).count() == 0 and skill_progress['current'] >= skill_progress['max']:
                self.add_completed_skill(skill, False)

    def add_completed_skill(self, skill, is_validated_through_test):
        from MookAPI.services import completed_skills
        if completed_skills.find(user=self, skill=skill).count() == 0:
            completed_skills.create(user=self, skill=skill, is_validated_through_test=is_validated_through_test)
            track = skill.track
            track_progress = track.user_progress(self)
            from MookAPI.services import unlocked_track_tests
            if unlocked_track_tests.find(user=self, track=track).count() == 0 and track_progress['current'] >= track_progress['max']:
                self.unlock_track_validation_test(track)

    def add_started_track(self, track):
        from MookAPI.services import started_tracks
        if started_tracks.find(user=self, track=track).count() == 0:
            started_tracks.create(user=self, track=track)

    def unlock_track_validation_test(self, track):
        from MookAPI.services import unlocked_track_tests
        if unlocked_track_tests.find(user=self, track=track).count() == 0:
            unlocked_track_tests.create(user=self, track=track)

    def add_completed_track(self, track):
        from MookAPI.services import completed_tracks
        if completed_tracks.find(user=self, track=track).count() == 0:
            completed_tracks.create(user=self, track=track)

    def is_track_test_available_and_never_attempted(self, track):
        # FIXME Make more efficient search using Service
        from MookAPI.services import unlocked_track_tests
        if unlocked_track_tests.find(user=self, track=track).count() > 0:
            from MookAPI.services import track_validation_attempts
            attempts = track_validation_attempts.find(user=self)
            return all(attempt.track != track for attempt in attempts)

        return False

    @staticmethod
    def hash_pass(password):
        """
        Return the md5 hash of the password+salt
        """
        return bcrypt.encrypt(password)

    def verify_pass(self, password):
        return bcrypt.verify(password, self.password)

    @property
    def url(self):
        return url_for("users.get_user_info", user_id=self.id, _external=True)

    def all_syncable_items(self, local_server=None):
        items = super(User, self).all_syncable_items()

        from MookAPI.services import activities
        for activity in activities.find(user=self):
            items.extend(activity.all_syncable_items(local_server=local_server))

        return items

    def __unicode__(self):
        return self.username or self.email or self.id
