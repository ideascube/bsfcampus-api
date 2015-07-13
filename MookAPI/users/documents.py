from passlib.hash import bcrypt
import bson

from flask import url_for

from MookAPI.core import db
from MookAPI.helpers import JsonSerializer
from MookAPI.sync import SyncableDocument

class RoleJsonSerializer(JsonSerializer):
    pass

class Role(RoleJsonSerializer, SyncableDocument):
    name = db.StringField(max_length=80, unique=True)

    description = db.StringField()

    def __unicode__(self):
        return self.name

class UserJsonSerializer(JsonSerializer):
    __json_additional__ = [
        'exercise_attempts',
        'skill_validation_attempts',
        'track_validation_attempts',
        'completed_resources',
        'completed_skills',
        'started_tracks',
        'unlocked_track_tests',
        'completed_tracks'
        ]

    @staticmethod
    def to_dbref_list(list, user):
        return [item.to_json_dbref() for item in list]

    @staticmethod
    def to_resources_dbref_list(list, user):
        return [item.resource.to_json_dbref() for item in list]

    @staticmethod
    def to_skills_dbref_list(list, user):
        return [item.skill.to_json_dbref() for item in list]

    @staticmethod
    def to_tracks_dbref_list(list, user):
        return [item.track.to_json_dbref() for item in list]

    __json_modifiers__ = dict(
        exercise_attempts=to_dbref_list.__func__,
        skill_validation_attempts=to_dbref_list.__func__,
        track_validation_attempts=to_dbref_list.__func__,
        completed_resources=to_resources_dbref_list.__func__,
        completed_skills=to_skills_dbref_list.__func__,
        started_tracks=to_tracks_dbref_list.__func__,
        unlocked_track_tests=to_tracks_dbref_list.__func__,
        completed_tracks=to_tracks_dbref_list.__func__
    )

class User(UserJsonSerializer, SyncableDocument):

    full_name = db.StringField(unique=False, required=True)

    username = db.StringField(unique=True, required=True)

    email = db.EmailField(unique=False)

    password = db.StringField()

    active = db.BooleanField(default=True)

    accept_cgu = db.BooleanField(required=True, default=False)

    roles = db.ListField(db.ReferenceField(Role))

    @property
    def exercise_attempts(self):
        from MookAPI.services import exercise_attempts
        return exercise_attempts.find(user=self)

    @property
    def skill_validation_attempts(self):
        from MookAPI.services import skill_validation_attempts
        return skill_validation_attempts.find(user=self)

    @property
    def track_validation_attempts(self):
        from MookAPI.services import track_validation_attempts
        return track_validation_attempts.find(user=self)

    @property
    def completed_resources(self):
        from MookAPI.services import completed_resources
        return completed_resources.find(user=self)

    @property
    def completed_skills(self):
        from MookAPI.services import completed_skills
        return completed_skills.find(user=self)

    @property
    def started_tracks(self):
        from MookAPI.services import started_tracks
        return started_tracks.find(user=self)

    @property
    def unlocked_track_tests(self):
        from MookAPI.services import unlocked_track_tests
        return unlocked_track_tests.find(user=self)

    @property
    def completed_tracks(self):
        from MookAPI.services import completed_tracks
        return completed_tracks.find(user=self)

    def add_completed_resource(self, resource):
        from MookAPI.services import completed_resources
        if completed_resources.find(user=self, resource=resource).count() == 0:
            completed_resources.create(user=self, resource=resource)
            skill = resource.parent.skill
            skill_progress = skill.user_progress(self)
            from MookAPI.services import completed_skills
            if completed_skills.find(user=self, skill=skill).count() == 0 and skill_progress['current'] >= skill_progress['max']:
                self.add_completed_skill(skill)

    def add_completed_skill(self, skill):
        from MookAPI.services import completed_skills
        if completed_skills.find(user=self, skill=skill).count() == 0:
            completed_skills.create(user=self, skill=skill)
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
            return all(attempted_test.exercise.parent != track for attempted_test in self.track_validation_attempts)

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

        for item in self.exercise_attempts:
            if local_server.syncs_document(item.exercise):
                items.extend(item.all_syncable_items(local_server=local_server))
        for item in self.skill_validation_attempts:
            if local_server.syncs_document(item.skill):
                items.extend(item.all_syncable_items(local_server=local_server))
        for item in self.track_validation_attempts:
            if local_server.syncs_document(item.track):
                items.extend(item.all_syncable_items(local_server=local_server))
        for item in self.completed_resources:
            if local_server.syncs_document(item.resource):
                items.extend(item.all_syncable_items(local_server=local_server))
        for item in self.completed_skills:
            if local_server.syncs_document(item.skill):
                items.extend(item.all_syncable_items(local_server=local_server))
        for item in self.started_tracks:
            if local_server.syncs_document(item.track):
                items.extend(item.all_syncable_items(local_server=local_server))
        for item in self.unlocked_track_tests:
            if local_server.syncs_document(item.track):
                items.extend(item.all_syncable_items(local_server=local_server))
        for item in self.completed_tracks:
            if local_server.syncs_document(item.track):
                items.extend(item.all_syncable_items(local_server=local_server))

        return items

    def __unicode__(self):
        return self.username or self.email or self.id
