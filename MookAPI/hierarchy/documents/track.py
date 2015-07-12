import random

from flask import url_for
from flask_jwt import current_user, verify_jwt

from MookAPI.core import db
from . import ResourceHierarchyJsonSerializer, ResourceHierarchy

class TrackJsonSerializer(ResourceHierarchyJsonSerializer):
    __json_additional__ = []
    __json_additional__.extend(ResourceHierarchyJsonSerializer.__json_additional__)
    __json_additional__.extend(['skills_refs', 'is_started', 'test_is_unlocked', 'validation_test'])
    __json_rename__ = dict(skills_refs='skills')

class Track(TrackJsonSerializer, ResourceHierarchy):
    """
    .. _Track:

    Top level of Resource_ hierarchy. Their descendants are Skill_ objects.
    """

    icon = db.ImageField()
    """An icon to illustrate the Track_."""

    @property
    def icon_url(self):
        """The URL where the track icon can be downloaded."""
        return url_for("hierarchy.get_track_icon", track_id=self.id, _external=True)

    bg_color = db.StringField()
    """The background color of pages in this Track_."""

    ### VIRTUAL PROPERTIES

    @property
    def url(self):
        return url_for("hierarchy.get_track", track_id=self.id, _external=True)

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
        user = current_user._get_current_object()
        return self.is_started_by_user(user)

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
        user = current_user._get_current_object()
        return self.test_is_unlocked_by_user(user)

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
    def breadcrumb(self):
        return [self.to_json_dbref()]

    ### METHODS

    def encode_mongo_for_dashboard(self, user):
        response = super(Track, self).encode_mongo_for_dashboard(user)
        response['icon_url'] = self.icon_url
        response['is_started'] = self.is_started_by_user(user)
        response['skills'] = [skill.encode_mongo_for_dashboard(user) for skill in self.skills]
        response['skills'].sort(key=lambda s: s['order'])

        return response

    def all_syncable_items(self):
        items = super(Track, self).all_syncable_items()

        for skill in self.skills:
            items.extend(skill.all_syncable_items())

        for test in self.track_validation_tests:
            items.extend(test.all_syncable_items())

        return items

    # @if_central
    def items_to_update(self, last_sync, local_server=None):
        items = super(Track, self).items_to_update(last_sync, local_server=local_server)

        for skill in self.skills:
            items.extend(skill.items_to_update(last_sync, local_server=local_server))

        for test in self.track_validation_tests:
            items.extend(test.all_syncable_items())

        return items
