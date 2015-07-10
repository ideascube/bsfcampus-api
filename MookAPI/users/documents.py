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
        # FIXME Make more efficient search using Service
        if resource not in [item.resource for item in self.completed_resources]:
            from MookAPI.services import completed_resources
            completed_resources.create(user=self, resource=resource)
            skill = resource.parent.skill
            skill_progress = skill.user_progress(self)
            # FIXME Make more efficient search using Service
            if skill not in [item.skill for item in self.completed_skills] and skill_progress['current'] >= skill_progress['max']:
                self.add_completed_skill(skill)

    def add_completed_skill(self, skill):
        # FIXME Make more efficient search using Service
        if skill not in [item.skill for item in self.completed_skills]:
            from MookAPI.services import completed_skills
            completed_skills.create(user=self, skill=skill)
            track = skill.track
            track_progress = track.user_progress(self)
            # FIXME Make more efficient search using Service
            if track not in [item.track for item in self.unlocked_track_tests] and track_progress['current'] >= track_progress['max']:
                self.unlock_track_validation_test(track)

    def add_started_track(self, track):
        # FIXME Make more efficient search using Service
        if track not in [item.track for item in self.started_tracks]:
            from MookAPI.services import started_tracks
            started_tracks.create(user=self, track=track)

    def unlock_track_validation_test(self, track):
        # FIXME Make more efficient search using Service
        if track not in [item.track for item in self.unlocked_track_tests]:
            from MookAPI.services import unlocked_track_tests
            unlocked_track_tests.create(user=self, track=track)

    def add_completed_track(self, track):
        # FIXME Make more efficient search using Service
        if track not in [item.track for item in self.completed_tracks]:
            from MookAPI.services import completed_tracks
            completed_tracks.create(user=self, track=track)

    def is_track_test_available_and_never_attempted(self, track):
        # FIXME Make more efficient search using Service
        if track in [item.track for item in self.unlocked_track_tests]:
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

    def all_syncable_items(self):
        items = super(User, self).all_syncable_items()

        for item in self.exercise_attempts:
            items.extend(item.all_syncable_items())
        for item in self.skill_validation_attempts:
            items.extend(item.all_syncable_items())
        for item in self.track_validation_attempts:
            items.extend(item.all_syncable_items())
        for item in self.completed_resources:
            items.extend(item.all_syncable_items())
        for item in self.completed_skills:
            items.extend(item.all_syncable_items())
        for item in self.started_tracks:
            items.extend(item.all_syncable_items())
        for item in self.unlocked_track_tests:
            items.extend(item.all_syncable_items())
        for item in self.completed_tracks:
            items.extend(item.all_syncable_items())

        return items

    # @if_central
    def items_to_update(self, last_sync):
        items = super(User, self).items_to_update(last_sync)

        for item in self.exercise_attempts:
            items.extend(item.items_to_update(last_sync))
        for item in self.skill_validation_attempts:
            items.extend(item.items_to_update(last_sync))
        for item in self.track_validation_attempts:
            items.extend(item.items_to_update(last_sync))
        for item in self.completed_resources:
            items.extend(item.items_to_update(last_sync))
        for item in self.completed_skills:
            items.extend(item.items_to_update(last_sync))
        for item in self.started_tracks:
            items.extend(item.items_to_update(last_sync))
        for item in self.unlocked_track_tests:
            items.extend(item.items_to_update(last_sync))
        for item in self.completed_tracks:
            items.extend(item.items_to_update(last_sync))

        return items

    def __unicode__(self):
        return self.username or self.email or self.id
