import random

from MookAPI import db, api
import MookAPI.resources.documents.track_validation
from . import ResourceHierarchy, skill
from flask_jwt import current_user
from .. import views

class Track(ResourceHierarchy):
    """
    .. _Track:

    Top level of Resource_ hierarchy. Their descendants are Skill_ objects.
    """

    icon = db.ImageField()
    """An icon to illustrate the Track_."""

    @property
    def icon_url(self):
        """The URL where the track icon can be downloaded."""
        return api.url_for(views.TrackIconView, track_id=self.id, _external=True)

    bg_color = db.StringField()
    """The background color of pages in this Track_."""

    ### VIRTUAL PROPERTIES

    @property
    def url(self):
        return api.url_for(views.TrackView, track_id=self.id, _external=True)

    @property
    def skills(self):
        """A queryset of the Skill_ objects that belong to the current Track_."""
        return skill.Skill.objects.order_by('order', 'title').filter(track=self)

    def is_validated(self, user):
        """Whether the current_user validated the hierarchy level based on their activity."""
        return self in user.completed_tracks

    def progress(self, user):
        current = 0
        for skill in self.skills:
            if skill.is_validated(user):
                current += 1
        return {'current': current, 'max': len(self.skills)}

    def is_started(self, user):
        return self in user.started_tracks

    @property
    def track_validation_tests(self):
        """A queryset of the TrackValidationResource_ objects that belong to the current Track_."""
        return MookAPI.resources.documents.track_validation.TrackValidationResource.objects.order_by('order', 'title').filter(parent=self)

    ### METHODS

    def breadcrumb(self):
        return [self._breadcrumb_item()]

    def encode_mongo(self):
        son = super(Track, self).encode_mongo()

        user = current_user._get_current_object()

        validation_tests = map(lambda t: t.id, self.track_validation_tests)
        if len(validation_tests) > 0:
            i = random.randrange(0, len(validation_tests))
            son['validation_test'] = validation_tests[i]
        son['skills'] = map(lambda s: s.id, self.skills)
        son['test_unlocked'] = self in user.unlocked_track_tests
        son['is_started'] = self.is_started(user)

        return son

    def encode_mongo_for_dashboard(self, user):
        response = super(Track, self).encode_mongo_for_dashboard(user)
        response['icon_url'] = self.icon_url
        response['is_started'] = self.is_started(user)
        response['skills'] = []
        for skill in self.skills:
            response['skills'].append(skill.encode_mongo_for_dashboard(user))
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
