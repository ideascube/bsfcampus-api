import random

from flask import url_for
from flask_jwt import current_user

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
        return self in user.completed_tracks

    def user_progress(self, user):
        current = 0
        for skill in self.skills:
            if skill.is_validated_by_user(user):
                current += 1
        return {'current': current, 'max': len(self.skills)}

    def is_started_by_user(self, user):
        return self in user.started_tracks

    @property
    def is_started(self):
        user = current_user._get_current_object()
        return self.is_started_by_user(user)

    def test_is_unlocked_by_user(self, user):
        return self in user.unlocked_track_tests

    @property
    def test_is_unlocked(self):
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
        return [self._breadcrumb_item()]

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

        return items

    # @if_central
    def items_to_update(self, last_sync):
        items = super(Track, self).items_to_update(last_sync)

        for skill in self.skills:
            items.extend(skill.items_to_update(last_sync))

        return items
