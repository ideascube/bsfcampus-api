from passlib.hash import bcrypt

from flask import url_for
from flask_login import UserMixin

from MookAPI.core import db
from MookAPI.sync import SyncableDocumentJsonSerializer, SyncableDocument
from MookAPI.serialization import CsvSerializer

from datetime import datetime

class RoleJsonSerializer(SyncableDocumentJsonSerializer):
    pass

class Role(RoleJsonSerializer, SyncableDocument):
    name = db.StringField(max_length=80, unique=True)

    description = db.StringField()

    def __unicode__(self):
        return self.name

class UserJsonSerializer(SyncableDocumentJsonSerializer):
    __json_dbref__ = ['full_name']
    __json_additional__ = [
        'tutors',
        'students',
        'awaiting_tutor_requests',
        'awaiting_student_requests',
        'pending_tutors',
        'pending_students',
        'not_acknowledged_tutors',
        'not_acknowledged_students',
        'all_credentials'
    ]

class User(UserJsonSerializer, CsvSerializer, SyncableDocument):

    full_name = db.StringField(unique=False, required=True)

    email = db.EmailField(unique=False)

    country = db.StringField()

    occupation = db.StringField()

    organization = db.StringField()

    active = db.BooleanField(default=True)

    accept_cgu = db.BooleanField(required=True, default=False)

    roles = db.ListField(db.ReferenceField(Role))

    @property
    def inscription_time(self):
        from MookAPI.services import misc_activities
        creation_activity = misc_activities.first(user=self, type="register_user_attempt", object_title="success")
        return creation_activity.date if creation_activity else "#NO INSCRIPTION DATE FOUND#"

    @property
    def inscription_date(self):
        inscription_date = self.inscription_time
        if isinstance(inscription_date, datetime):
             inscription_date = inscription_date.strftime("%Y-%m-%d")
        return inscription_date

    @property
    def tracks(self):
        from MookAPI.services import completed_tracks
        completedTracks = completed_tracks.__model__.objects(user=self).only('track').distinct('track')
        return "|".join(
            track.title for track in completedTracks
        )

    @property
    def skills(self):
        from MookAPI.services import completed_skills
        completedSkills = completed_skills.__model__.objects(user=self).only('skill').distinct('skill')
        return "|".join(
            skill.title for skill in completedSkills
        )

    def courses_info(self, analytics=False):
        info = dict(
            tracks=dict(),
            skills=dict(),
            resources=dict()
        )

        from MookAPI.services import tracks
        for track in tracks.all():
            info['tracks'][str(track.id)] = track.user_info(user=self, analytics=analytics)
            for skill in track.skills:
                info['skills'][str(skill.id)] = skill.user_info(user=self, analytics=analytics)
                for lesson in skill.lessons:
                    for resource in lesson.resources:
                        info['resources'][str(resource.id)] = resource.user_info(user=self, analytics=analytics)

        return info


    @property
    def tutors(self):
        from MookAPI.services import tutoring_relations
        relations = tutoring_relations.find(student=self, accepted=True)
        return [relation.tutor for relation in relations]
    
    @property
    def students(self):
        from MookAPI.services import tutoring_relations
        relations = tutoring_relations.find(tutor=self, accepted=True)
        return [relation.student for relation in relations]

    ## Awaiting: the current user was requested
    @property
    def awaiting_tutor_requests(self):
        from MookAPI.services import tutoring_relations
        relations = tutoring_relations.find(
            tutor=self,
            initiated_by='student',
            accepted=False
        )
        return [relation.student for relation in relations]

    @property
    def awaiting_student_requests(self):
        from MookAPI.services import tutoring_relations
        relations = tutoring_relations.find(
            student=self,
            initiated_by='tutor',
            accepted=False
        )
        return [relation.tutor for relation in relations]

    ## Not acknowledged: Requests initiated by the current user have been accepted
    @property
    def not_acknowledged_tutors(self):
        from MookAPI.services import tutoring_relations
        relations = tutoring_relations.find(
            student=self,
            initiated_by='student',
            accepted=True,
            acknowledged=False
        )
        return [relation.tutor for relation in relations]

    @property
    def not_acknowledged_students(self):
        from MookAPI.services import tutoring_relations
        relations = tutoring_relations.find(
            tutor=self,
            initiated_by='tutor',
            accepted=True,
            acknowledged=False
        )
        return [relation.student for relation in relations]

    ## Pending: the current user made the request
    @property
    def pending_tutors(self):
        from MookAPI.services import tutoring_relations
        relations = tutoring_relations.find(
            student=self,
            initiated_by='student',
            accepted=False
        )
        return [relation.tutor for relation in relations]

    @property
    def pending_students(self):
        from MookAPI.services import tutoring_relations
        relations = tutoring_relations.find(
            tutor=self,
            initiated_by='tutor',
            accepted=False
        )
        return [relation.student for relation in relations]

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
            unlocked_track_tests
        skills = set()
        tracks = set()
        for activity in completed_resources.find(user=self):
            skills.add(activity.resource.skill)
        for skill in skills:
            tracks.add(skill.track)
        for track in tracks:
            track_progress = track.user_progress(self)
            if unlocked_track_tests.find(user=self, track=track).count() == 0 and track_progress['current'] >= track_progress['max']:
                self_credentials.unlock_track_validation_test(track)

    @property
    def url(self, _external=False):
        return url_for("users.get_user_info", user_id=self.id, _external=_external)

    @property
    def username(self):
        credentials = self.all_credentials
        if not credentials:
            return "#NO USERNAME FOUND#"
        return credentials[0].username

    @property
    def all_credentials(self):
        from MookAPI.services import user_credentials
        return user_credentials.find(user=self)

    def credentials(self, local_server=None):
        from MookAPI.services import user_credentials
        return user_credentials.find(user=self, local_server=local_server)


    def all_synced_documents(self, local_server=None):
        items = super(User, self).all_synced_documents()

        from MookAPI.services import activities, tutoring_relations
        for creds in self.credentials(local_server=local_server):
            items.extend(creds.all_synced_documents(local_server=local_server))
        for activity in activities.find(user=self):
            items.extend(activity.all_synced_documents(local_server=local_server))
        for student_relation in tutoring_relations.find(tutor=self):
            items.extend(student_relation.all_synced_documents(local_server=local_server))
        for tutor_relation in tutoring_relations.find(student=self):
            items.extend(tutor_relation.all_synced_documents(local_server=local_server))

        return items

    def __unicode__(self):
        return self.full_name or self.email or self.id

    def phagocyte(self, other, self_credentials):
        if other == self:
            self.update_progress(self_credentials)
            self.save()
            return self

        from MookAPI.services import \
            activities, \
            tutoring_relations, \
            user_credentials
        for creds in user_credentials.find(user=other):
            creds.user = self
            creds.save(validate=False)
        for activity in activities.find(user=other):
            activity.user = self
            activity.save()
        for student_relation in tutoring_relations.find(tutor=other):
            student_relation.tutor = self
            student_relation.save()
        for tutor_relation in tutoring_relations.find(student=other):
            tutor_relation.student = self
            tutor_relation.save()

        other.active = False
        other.phagocyted_by = self
        other.save()

        self.update_progress(self_credentials)
        self.save()

        return self

    @classmethod
    def field_names_header_for_csv(cls):
        return ['Full name', 'Username', 'Email', 'Country', 'Occupation', 'Organization', 'Inscription date', 'Tracks', 'Skills']

    def get_field_names_for_csv(cls):
        return 'full_name username email country occupation organization inscription_date tracks skills'.split()

class UserCredentialsJsonSerializer(SyncableDocumentJsonSerializer):
    __json_dbref__ = ["username", "local_server_name"]


class UserCredentials(UserCredentialsJsonSerializer,
                      SyncableDocument,
                      UserMixin):

    user = db.ReferenceField(User, required=True)

    local_server = db.ReferenceField('LocalServer', required=False)

    @property
    def local_server_name(self):
        if self.local_server:
            return self.local_server.name
        return None

    username = db.StringField(unique_with='local_server', required=True)

    password = db.StringField()

    @property
    def is_active(self):
        return self.user.active

    def has_role(self, rolename):
        return rolename in [r.name for r in self.user.roles]

    def add_visited_resource(self, resource):
        achievements = []
        from MookAPI.services import exercise_resources, video_resources, external_video_resources, visited_resources
        visited_resource = visited_resources.create(credentials=self, resource=resource)
        if not resource.is_additional:
            track_achievements = self.add_started_track(resource.track)
            achievements.extend(track_achievements)
            if not exercise_resources._isinstance(resource) and not video_resources._isinstance(resource) and not external_video_resources._isinstance(resource):
                resource_achievements = self.add_completed_resource(resource)
                achievements.extend(resource_achievements)
        return visited_resource, achievements

    def add_completed_resource(self, resource):
        achievements = []
        from MookAPI.services import completed_resources
        if completed_resources.find(user=self.user, resource=resource).count() == 0:
            completed_resource = completed_resources.create(
                credentials=self,
                resource=resource
            )
            achievements.append(completed_resource)
        return achievements

    def add_completed_skill(self, skill):
        achievements = []
        from MookAPI.services import completed_skills
        if completed_skills.find(user=self.user,
                                 skill=skill,
                                 is_validated_through_test=True).count() == 0:
            completed_skill = completed_skills.create(
                credentials=self,
                skill=skill,
                is_validated_through_test=True
            )
            achievements.append(completed_skill)
            track = skill.track
            track_progress = track.user_progress(self.user)
            from MookAPI.services import unlocked_track_tests
            if unlocked_track_tests.find(user=self.user, track=track).count() == 0 and track_progress['current'] >= track_progress['max']:
                track_achievements = self.unlock_track_validation_test(track=track)
                achievements.extend(track_achievements)
        return achievements

    def add_started_track(self, track):
        achievements = []
        from MookAPI.services import started_tracks
        if started_tracks.find(user=self.user, track=track).count() == 0:
            started_track = started_tracks.create(credentials=self, track=track)
            achievements.append(started_track)
        return achievements


    def unlock_track_validation_test(self, track):
        achievements = []
        from MookAPI.services import unlocked_track_tests
        if unlocked_track_tests.find(user=self.user, track=track).count() == 0:
            unlocked_track_test = unlocked_track_tests.create(credentials=self, track=track)
            achievements.append(unlocked_track_test)
        return achievements


    def add_completed_track(self, track):
        achievements = []
        from MookAPI.services import completed_tracks
        if completed_tracks.find(user=self.user, track=track).count() == 0:
            completed_track = completed_tracks.create(credentials=self, track=track)
            achievements.append(completed_track)
        return achievements

    def is_track_test_available_and_never_attempted(self, track):
        return self.user.is_track_test_available_and_never_attempted(track)

    @property
    def url(self, _external=False):
        return url_for("users.get_user_credentials", credentials_id=self.id, _external=_external)

    @staticmethod
    def hash_pass(password):
        """
        Return the md5 hash of the password+salt
        """
        return bcrypt.encrypt(password)

    def verify_pass(self, password):
        return bcrypt.verify(password, self.password)
