from passlib.hash import bcrypt

from flask import url_for

from MookAPI.core import db
from MookAPI.sync import SyncableDocumentJsonSerializer, SyncableDocument

class RoleJsonSerializer(SyncableDocumentJsonSerializer):
    pass

class Role(RoleJsonSerializer, SyncableDocument):
    name = db.StringField(max_length=80, unique=True)

    description = db.StringField()

    def __unicode__(self):
        return self.name

class UserJsonSerializer(SyncableDocumentJsonSerializer):
    __json_dbref__ = ['full_name']

class User(UserJsonSerializer, SyncableDocument):

    full_name = db.StringField(unique=False, required=True)

    email = db.EmailField(unique=False)

    active = db.BooleanField(default=True)

    accept_cgu = db.BooleanField(required=True, default=False)

    roles = db.ListField(db.ReferenceField(Role))

    tutors = db.ListField(db.ReferenceField('self'))

    tutored_students = db.ListField(db.ReferenceField('self'))

    awaiting_tutor_requests = db.ListField(db.ReferenceField('self'))

    awaiting_student_requests = db.ListField(db.ReferenceField('self'))

    phagocyted_by = db.ReferenceField('self', required=False)

    def is_track_test_available_and_never_attempted(self, track):
        # FIXME Make more efficient search using Service
        from MookAPI.services import unlocked_track_tests
        if unlocked_track_tests.find(user=self, track=track).count() > 0:
            from MookAPI.services import track_validation_attempts
            attempts = track_validation_attempts.find(user=self)
            return all(attempt.track != track for attempt in attempts)

        return False

    def update_progress(self, self_credentials):
        from MookAPI.services import \
            completed_resources, \
            completed_skills, \
            unlocked_track_tests
        skills = []
        tracks = []
        for activity in completed_resources.find(user=self):
            if activity.resource.skill not in skills:
                skills.append(activity.resource.skill)
        for skill in skills:
            if skill.track not in tracks:
                tracks.append(skill.track)
            skill_progress = skill.user_progress(self)
            if completed_skills.find(user=self, skill=skill).count() == 0 and skill_progress['current'] >= skill_progress['max']:
                self_credentials.add_completed_skill(skill, False)
        for track in tracks:
            track_progress = track.user_progress(self)
            if unlocked_track_tests.find(user=self, track=track).count() == 0 and track_progress['current'] >= track_progress['max']:
                self_credentials.unlock_track_validation_test(track)

    @property
    def url(self):
        return url_for("users.get_user_info", user_id=self.id, _external=True)

    def all_syncable_items(self, local_server=None):
        items = super(User, self).all_syncable_items()

        from MookAPI.services import user_credentials, activities
        for creds in user_credentials.find(user=self):
            items.extend(creds.all_syncable_items(local_server=local_server))
        for activity in activities.find(user=self):
            items.extend(activity.all_syncable_items(local_server=local_server))

        return items

    def __unicode__(self):
        return self.full_name or self.email or self.id

    def phagocyte(self, other, self_credentials):
        if other == self:
            self.update_progress(self_credentials)
            self.save()
            return self

        from MookAPI.services import users, user_credentials, activities
        for creds in user_credentials.find(user=other):
            creds.user = self
            creds.save(validate=False)
        for activity in activities.find(user=other):
            activity.user = self
            activity.save()
        for user in users.find(tutors=other):
            user.tutors.remove(other)
            user.tutors.append(self)
            user.tutors.save()
        for user in users.find(tutored_students=other):
            user.tutored_students.remove(other)
            user.tutored_students.append(self)
            user.tutors.save()
        for user in users.find(awaiting_tutor_requests=other):
            user.awaiting_tutor_requests.remove(other)
            user.awaiting_tutor_requests.append(self)
            user.awaiting_tutor_requests.save()
        for user in users.find(awaiting_student_requests=other):
            user.awaiting_student_requests.remove(other)
            user.awaiting_student_requests.append(self)
            user.awaiting_student_requests.save()

        other.active = False
        other.phagocyted_by = self
        other.save()

        self.update_progress(self_credentials)
        self.save()

        return self


class UserCredentialsJsonSerializer(SyncableDocumentJsonSerializer):
    pass

class UserCredentials(SyncableDocument):

    user = db.ReferenceField(User, required=True)

    local_server = db.ReferenceField('LocalServer', required=False)

    username = db.StringField(unique_with='local_server', required=True)

    password = db.StringField()

    def add_completed_resource(self, resource):
        from MookAPI.services import completed_resources
        if completed_resources.find(user=self.user, resource=resource).count() == 0:
            completed_resources.create(credentials=self, resource=resource)
            skill = resource.parent.skill
            skill_progress = skill.user_progress(self.user)
            from MookAPI.services import completed_skills
            if completed_skills.find(user=self.user, skill=skill).count() == 0 and skill_progress['current'] >= skill_progress['max']:
                self.add_completed_skill(skill=skill, is_validated_through_test=False)

    def add_completed_skill(self, skill, is_validated_through_test):
        from MookAPI.services import completed_skills
        if completed_skills.find(user=self.user, skill=skill).count() == 0:
            completed_skills.create(credentials=self, skill=skill, is_validated_through_test=is_validated_through_test)
            track = skill.track
            track_progress = track.user_progress(self.user)
            from MookAPI.services import unlocked_track_tests
            if unlocked_track_tests.find(user=self.user, track=track).count() == 0 and track_progress['current'] >= track_progress['max']:
                self.unlock_track_validation_test(track)

    def add_started_track(self, track):
        from MookAPI.services import started_tracks
        if started_tracks.find(user=self.user, track=track).count() == 0:
            started_tracks.create(credentials=self, track=track)

    def unlock_track_validation_test(self, track):
        from MookAPI.services import unlocked_track_tests
        if unlocked_track_tests.find(user=self.user, track=track).count() == 0:
            unlocked_track_tests.create(credentials=self, track=track)

    def add_completed_track(self, track):
        from MookAPI.services import completed_tracks
        if completed_tracks.find(user=self.user, track=track).count() == 0:
            completed_tracks.create(credentials=self, track=track)

    def is_track_test_available_and_never_attempted(self, track):
        return self.user.is_track_test_available_and_never_attempted(track)

    @property
    def url(self):
        return url_for("users.get_user_credentials", credentials_id=self.id, _external=True)

    @staticmethod
    def hash_pass(password):
        """
        Return the md5 hash of the password+salt
        """
        return bcrypt.encrypt(password)

    def verify_pass(self, password):
        return bcrypt.verify(password, self.password)
