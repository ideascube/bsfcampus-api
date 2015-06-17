from MookAPI import db, api
import MookAPI.resources.documents
from . import ResourceHierarchy
from .. import views

class Lesson(ResourceHierarchy):
    """
    .. _Lesson:

    Third level of resources hierarchy. Their ascendants are Skill_ objects.
    Resource_ objects reference a parent Lesson_.
    """

    ### PROPERTIES

    skill = db.ReferenceField('Skill')
    """The parent Skill_."""

    ### VIRTUAL PROPERTIES

    @property
    def track(self):
        """Shorthand virtual property to the parent Track_ of the parent Skill_."""
        return self.skill.track

    @property
    def url(self):
        return api.url_for(views.LessonView, lesson_id=self.id, _external=True)

    @property
    def resources(self):
        """A queryset of the Resource_ objects that belong to the current Lesson_."""
        return MookAPI.resources.documents.Resource.objects.order_by('order', 'title').filter(parent=self)

    @property
    def progress(self):
        current = 0
        for resource in self.resources:
            if resource.is_validated:
                current += 1
        return {'current': current, 'max': len(self.resources)}

    ### METHODS

    def breadcrumb(self):
        return [
            self.track._breadcrumb_item(),
            self.skill._breadcrumb_item(),
            self._breadcrumb_item()
            ]

    def siblings(self):
        return Lesson.objects.order_by('order', 'title').filter(skill=self.skill)

    def siblings_strict(self):
        return Lesson.objects.order_by('order', 'title').filter(skill=self.skill, id__ne=self.id)

    def encode_mongo(self):
        son = super(Lesson, self).encode_mongo()

        son['resources'] = map(lambda r: r.id, self.resources)

        return son

    def top_level_syncable_document(self):
        return self.track

    def all_syncable_items(self):
        items = super(Lesson, self).all_syncable_items()

        for resource in self.resources:
            items.extend(resource.all_syncable_items())

        return items

    # @if_central
    def items_to_update(self, last_sync):
        items = super(Lesson, self).items_to_update(last_sync)

        for resource in self.resources:
            items.extend(resource.items_to_update(last_sync))

        return items

