import random
import datetime
import math

from flask import url_for
from flask_jwt import current_user, verify_jwt

from MookAPI.core import db
from . import ResourceHierarchyJsonSerializer, ResourceHierarchy


class TrackJsonSerializer(ResourceHierarchyJsonSerializer):
    __json_additional__ = []
    __json_additional__.extend(ResourceHierarchyJsonSerializer.__json_additional__)
    __json_additional__.extend(['skills_refs', 'is_started', 'test_is_unlocked', 'validation_test'])
    __json_rename__ = dict(skills_refs='skills')
    __json_hierarchy_skeleton__ = ['skills']


class Track(TrackJsonSerializer, ResourceHierarchy):
    """
    .. _Track:

    Top level of Resource_ hierarchy. Their descendants are Skill_ objects.
    """

    icon = db.ImageField()
    """An icon to illustrate the Track_."""

    @property
    def icon_url(self, _external=True):
        """The URL where the track icon can be downloaded."""
        return url_for("hierarchy.get_track_icon", track_id=self.id, _external=_external)

    ### VIRTUAL PROPERTIES

    @property
    def url(self, _external=False):
        return url_for("hierarchy.get_track", track_id=self.id, _external=_external)

    @property
    def skills(self):
        """A queryset of the Skill_ objects that belong to the current Track_."""
        from MookAPI.services import skills

        return skills.find(track=self).order_by('order', 'title')

    @property
    def skills_refs(self):
        return [skill.to_json_dbref() for skill in self.skills]

    def is_validated_by_user(self, user):
        """Whether the user validated the hierarchy level based on their activity."""
        from MookAPI.services import completed_tracks

        return completed_tracks.find(track=self, user=user).count() > 0

    def user_progress(self, user):
        current = 0
        for skill in self.skills:
            if skill.is_validated_by_user(user):
                current += 1
        return {'current': current, 'max': len(self.skills)}

    def is_started_by_user(self, user):
        from MookAPI.services import started_tracks

        return started_tracks.find(track=self, user=user).count() > 0

    @property
    def is_started(self):
        try:
            verify_jwt()
        except:
            pass
        if not current_user:
            return None
        return self.is_started_by_user(current_user.user)

    def test_is_unlocked_by_user(self, user):
        from MookAPI.services import unlocked_track_tests

        return unlocked_track_tests.find(track=self, user=user).count() > 0

    @property
    def test_is_unlocked(self):
        try:
            verify_jwt()
        except:
            pass
        if not current_user:
            return None
        return self.test_is_unlocked_by_user(current_user.user)

    @property
    def track_validation_tests(self):
        """A queryset of the TrackValidationResource_ objects that belong to the current Track_."""
        from MookAPI.services import track_validation_resources

        return track_validation_resources.find(parent=self).order_by('order', 'title')

    @property
    def validation_test(self):
        number_of_tests = len(self.track_validation_tests)
        if len(self.track_validation_tests) > 0:
            i = random.randrange(0, number_of_tests)
            return self.track_validation_tests[i].to_json_dbref()
        return None

    @property
    def hierarchy(self):
        return [self.to_json_dbref()]

    ### METHODS

    def user_analytics(self, user):
        analytics = super(Track, self).user_analytics(user)

        from MookAPI.services import track_validation_attempts, visited_tracks

        track_validation_attempts = track_validation_attempts.find(user=user).order_by('-date')
        analytics['last_attempts_scores'] = map(
            lambda a: {"date": a.date, "nb_questions": a.nb_questions, "score": a.nb_right_answers},
            track_validation_attempts[:5]
        )

        nb_finished_attempts = 0
        total_duration = datetime.timedelta(0)
        for attempt in track_validation_attempts:
            if attempt.duration:
                nb_finished_attempts += 1
                total_duration += attempt.duration
        if nb_finished_attempts > 0:
            analytics['average_time_on_exercise'] = math.floor((total_duration / nb_finished_attempts).total_seconds())
        else:
            analytics['average_time_on_exercise'] = 0

        analytics['nb_attempts'] = track_validation_attempts.count()
        analytics['nb_visits'] = visited_tracks.find(user=user, track=self).count()

        return analytics

    def user_info(self, user, analytics=False):
        rv = super(Track, self).user_info(user=user, analytics=analytics)

        rv['is_started'] = self.is_started_by_user(user)
        rv['test_is_unlocked'] = self.test_is_unlocked_by_user(user)

        return rv

    def all_synced_documents(self, local_server=None):
        items = super(Track, self).all_synced_documents(local_server=local_server)

        for skill in self.skills:
            items.extend(skill.all_synced_documents(local_server=local_server))

        for test in self.track_validation_tests:
            items.extend(test.all_synced_documents(local_server=local_server))

        return items

    @classmethod
    def pre_delete(cls, sender, document, **kwargs):
        from MookAPI.services import local_servers
        for local_server in local_servers.find(synced_tracks=document):
            # The track is automatically pulled from the local server's sync list
            # thanks to the "reverse_delete_rule=PULL" option.
            # We just need to save the LS in order to update its LS last modification date
            local_server.save()

from mongoengine.signals import pre_delete
pre_delete.connect(Track.pre_delete, sender=Track)
