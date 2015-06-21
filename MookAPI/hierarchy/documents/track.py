import random

from MookAPI import db, api
import MookAPI.resources.documents.track_validation
from . import ResourceHierarchy, skill
import flask.ext.security as security
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

    @property
    def is_validated(self):
        """Whether the current_user validated the hierarchy level based on their activity."""
        return self in security.current_user.completed_tracks

    @property
    def progress(self):
        current = 0
        for skill in self.skills:
            if skill.is_validated:
                current += 1
        return {'current': current, 'max': len(self.skills)}

    @property
    def is_started(self):
        return self in security.current_user.started_tracks

    @property
    def track_validation_tests(self):
        """A queryset of the TrackValidationResource_ objects that belong to the current Track_."""
        return MookAPI.resources.documents.track_validation.TrackValidationResource.objects.order_by('order', 'title').filter(parent=self)

    ### METHODS

    def breadcrumb(self):
        return [self._breadcrumb_item()]

    def encode_mongo(self):
        son = super(Track, self).encode_mongo()

        validation_tests = map(lambda t: t.id, self.track_validation_tests)
        if len(validation_tests) > 0:
            i = random.randrange(0, len(validation_tests))
            son['validation_test'] = validation_tests[i]
        son['skills'] = map(lambda s: s.id, self.skills)
        son['test_unlocked'] = self in security.current_user.unlocked_track_tests
        son['is_started'] = self.is_started

        return son

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
