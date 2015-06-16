import bson
from MookAPI import db, api
from . import ResourceHierarchy, lesson, skill_validation
from MookAPI.resources.documents.exercise import ExerciseResource
import flask.ext.security as security
from .. import views

class Skill(ResourceHierarchy):
    """
    .. _Skill:

    Second level of Resource_ hierarchy.
    Their ascendants are Track_ objects.
    Their descendants are Lesson_ objects.
    """

    ### PROPERTIES

    ## Parent track
    track = db.ReferenceField('Track')
    """The parent Track_."""

    ## icon image
    icon = db.ImageField()
    """An icon to illustrate the Skill_."""

    ## short description
    short_description = db.StringField()
    """The short description of the skill, to appear where there is not enough space for the long one."""

    ## skill validation test
    validation_exercise = db.EmbeddedDocumentField(skill_validation.SkillValidationExercise)
    """The exercise that the user might take to validate the skill."""

    def _add_instance(self, obj):
        """This is a hack to provide the ``_instance`` property to the shorthand question-getters."""

        def _add_instance_single_object(obj):
            obj._instance = self
            return obj

        if isinstance(obj, list):
            return map(_add_instance_single_object, obj)
        else:
            return _add_instance_single_object(obj)

    @property
    def icon_url(self):
        """The URL where the skill icon can be downloaded."""
        return api.url_for(views.SkillIconView, skill_id=self.id, _external=True)

    ### VIRTUAL PROPERTIES

    @property
    def url(self):
        return api.url_for(views.SkillView, skill_id=self.id, _external=True)

    @property
    def lessons(self):
        """A queryset of the Lesson_ objects that belong to the current Skill_."""
        return lesson.Lesson.objects.order_by('order', 'title').filter(skill=self)

    @property
    def is_validated(self):
        """Whether the current_user validated the hierarchy level based on their activity."""
        return self in security.current_user.completed_skills

    @property
    def progress(self):
        current = 0
        nb_resources = 0
        for lesson in self.lessons:
            for resource in lesson.resources:
                nb_resources += 1
                if resource.is_validated:
                    current += 1
        return {'current': current, 'max': nb_resources}


    ### METHODS

    def breadcrumb(self):
        return [
            self.track._breadcrumb_item(),
            self._breadcrumb_item()
            ]

    def encode_mongo(self):
        son = super(Skill, self).encode_mongo()

        son['lessons'] = map(lambda l: l.id, self.lessons)
        son['bg_color'] = self.track.bg_color

        return son

    def top_level_syncable_document(self):
        return self.track

    def all_syncable_items(self):
        items = super(Skill, self).all_syncable_items()

        for lesson in self.lessons:
            items.extend(lesson.all_syncable_items())

        return items

    # @if_central
    def items_to_update(self, last_sync):
        items = super(Skill, self).items_to_update(last_sync)

        for lesson in self.lessons:
            items.extend(lesson.items_to_update(last_sync))

        return items

    @property
    def questions(self):
        """A list of all children exercises' questions, whatever their type."""

        questions = []
        for l in self.lessons:
            for r in l.resources:
                if isinstance(r, ExerciseResource):
                    questions.extend(r.questions)

        return questions

    def question(self, question_id):
        """A shorthand getter for a question with a known `_id`."""

        oid = bson.ObjectId(question_id)
        for l in self.lessons:
            for r in l.resources:
                if isinstance(r, ExerciseResource):
                    for q in r.questions:
                        if q._id == oid:
                            return r._add_instance(q)
        return None

    def random_questions(self, number=None):
        """
        A shorthand getter for a list of random questions.
        See the documentation of `SkillValidationExercise.random_questions`.
        """

        questions = self.validation_exercise.random_questions(self, number)
        return self._add_instance(questions)
