from flask import url_for

from MookAPI.core import db
import MookAPI.resources.documents
from . import ResourceHierarchyJsonSerializer, ResourceHierarchy


class LessonJsonSerializer(ResourceHierarchyJsonSerializer):
    __json_additional__ = []
    __json_additional__.extend(ResourceHierarchyJsonSerializer.__json_additional__)
    __json_additional__.extend(['resources_refs'])
    __json_rename__ = dict(resources_refs='resources')
    __json_hierarchy_skeleton__ = ['resources']

class Lesson(LessonJsonSerializer, ResourceHierarchy):
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
        return url_for("hierarchy.get_lesson", lesson_id=self.id, _external=True)

    @property
    def resources(self):
        """A queryset of the Resource_ objects that belong to the current Lesson_."""
        return MookAPI.resources.documents.Resource.objects.order_by('order', 'title').filter(parent=self)

    @property
    def resources_refs(self):
        return [resource.to_json_dbref() for resource in self.resources]

    def user_progress(self, user):
        current = 0
        for resource in self.resources:
            if resource.is_validated_by_user(user):
                current += 1
        return {'current': current, 'max': len(self.resources)}

    @property
    def hierarchy(self):
        return [
            self.track.to_json_dbref(),
            self.skill.to_json_dbref(),
            self.to_json_dbref()
            ]

    ### METHODS

    def siblings(self):
        return Lesson.objects.order_by('order', 'title').filter(skill=self.skill)

    def siblings_strict(self):
        return Lesson.objects.order_by('order', 'title').filter(skill=self.skill, id__ne=self.id)

    def encode_mongo_for_dashboard(self, user):
        response = super(Lesson, self).encode_mongo_for_dashboard(user)
        response['resources'] = []
        for resource in self.resources:
            response['resources'].append(resource.encode_mongo_for_dashboard(user))
        response['resources'].sort(key=lambda r: r['order'])

        return response

    def top_level_syncable_document(self):
        return self.track

    def all_syncable_items(self, local_server=None):
        items = super(Lesson, self).all_syncable_items(local_server=local_server)

        for resource in self.resources:
            items.extend(resource.all_syncable_items(local_server=local_server))

        return items

