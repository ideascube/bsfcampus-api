import bson
import random
import datetime
import math

from flask import url_for

from MookAPI.core import db
from MookAPI.serialization import JsonSerializer
from . import ResourceHierarchyJsonSerializer, ResourceHierarchy


class SkillValidationExerciseJsonSerializer(JsonSerializer):
    pass


class SkillValidationExercise(SkillValidationExerciseJsonSerializer, db.EmbeddedDocument):
    number_of_questions = db.IntField()
    """The number of questions to ask from this exercise."""

    max_mistakes = db.IntField()
    """The number of mistakes authorized before failing the exercise."""

    def random_questions(self, skill, number=None):
        """
        A list of random questions picked from the skill's children exercises.
        If `number` is not specified, it will be set to the skillValidationExercise's `number_of_questions` property.
        The list will contain `number` questions, or all questions if there are not enough questions in the exercise.
        """

        if not number:
            number = self.number_of_questions

        all_questions = skill.questions
        random.shuffle(all_questions)
        return all_questions[:number]


class SkillJsonSerializer(ResourceHierarchyJsonSerializer):
    __json_additional__ = []
    __json_additional__.extend(ResourceHierarchyJsonSerializer.__json_additional__)
    __json_additional__.extend(['lessons_refs'])
    __json_rename__ = dict(lessons_refs='lessons')
    __json_hierarchy_skeleton__ = ['lessons']


class Skill(SkillJsonSerializer, ResourceHierarchy):
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
    validation_exercise = db.EmbeddedDocumentField(SkillValidationExercise)
    """The exercise that the user might take to validate the skill."""

    ### VIRTUAL PROPERTIES

    @property
    def icon_url(self):
        """The URL where the skill icon can be downloaded."""
        return url_for("hierarchy.get_skill_icon", skill_id=self.id, _external=True)

    @property
    def url(self):
        return url_for("hierarchy.get_skill", skill_id=self.id, _external=True)

    @property
    def lessons(self):
        """A queryset of the Lesson_ objects that belong to the current Skill_."""
        from MookAPI.services import lessons

        return lessons.find(skill=self).order_by('order', 'title')

    @property
    def lessons_refs(self):
        return [lesson.to_json_dbref() for lesson in self.lessons]

    def is_validated_by_user(self, user):
        """Whether the current_user validated the hierarchy level based on their activity."""
        from MookAPI.services import completed_skills

        return completed_skills.find(skill=self, user=user).count() > 0

    def user_progress(self, user):
        current = 0
        nb_resources = 0
        for lesson in self.lessons:
            for resource in lesson.resources:
                nb_resources += 1
                if resource.is_validated_by_user(user):
                    current += 1
        return {'current': current, 'max': nb_resources}

    @property
    def bg_color(self):
        return self.track.bg_color

    @property
    def breadcrumb(self):
        return [
            self.track.to_json_dbref(),
            self.to_json_dbref()
        ]

    ### METHODS

    def _add_instance(self, obj):
        """This is a hack to provide the ``_instance`` property to the shorthand question-getters."""

        def _add_instance_single_object(obj):
            obj._instance = self
            return obj

        if isinstance(obj, list):
            return map(_add_instance_single_object, obj)
        else:
            return _add_instance_single_object(obj)

    def encode_mongo_for_dashboard(self, user):
        response = super(Skill, self).encode_mongo_for_dashboard(user)
        response['icon_url'] = self.icon_url
        response['short_description'] = self.short_description
        response['lessons'] = []
        for lesson in self.lessons:
            response['lessons'].append(lesson.encode_mongo_for_dashboard(user))
        response['lessons'].sort(key=lambda l: l['order'])

        from MookAPI.services import skill_validation_attempts, completed_skills, visited_skills

        if 'analytics' not in response:
            response['analytics'] = {}
        response['analytics']['progress'] = self.user_progress(user)
        skill_validation_attempts = skill_validation_attempts.find(user=user).order_by('-date')
        response['analytics']['last_attempts_scores'] = map(
            lambda a: {"date": a.date, "nb_questions": a.nb_questions, "score": a.nb_right_answers},
            skill_validation_attempts[:5])

        nb_finished_attempts = 0
        total_duration = datetime.timedelta(0)
        for i in range(len(skill_validation_attempts)):
            attempt = skill_validation_attempts[i]
            if attempt.duration:
                nb_finished_attempts += 1
                total_duration += attempt.duration
        if nb_finished_attempts > 0:
            response['analytics']['average_time_on_exercise'] = math.floor((total_duration / nb_finished_attempts).total_seconds())
        else:
            response['analytics']['average_time_on_exercise'] = 0

        response['analytics']['nb_attempts'] = len(skill_validation_attempts)
        completed_skill = completed_skills.first(user=user, skill=self)
        if completed_skill:
            response['analytics']['is_completed_through_test'] = completed_skill.is_validated_through_test
        response['analytics']['nb_visit'] = visited_skills.find(user=user, skill=self).count()

        return response

    def top_level_syncable_document(self):
        return self.track

    def all_syncable_items(self, local_server=None):
        items = super(Skill, self).all_syncable_items(local_server=local_server)

        for lesson in self.lessons:
            items.extend(lesson.all_syncable_items(local_server=local_server))

        return items

    @property
    def questions(self):
        """A list of all children exercises' questions, whatever their type."""

        from MookAPI.services import exercise_resources

        questions = []
        for l in self.lessons:
            for r in l.resources:
                if exercise_resources._isinstance(r):
                    questions.extend(r.questions)

        return questions

    def question(self, question_id):
        """A shorthand getter for a question with a known `_id`."""

        from MookAPI.services import exercise_resources

        oid = bson.ObjectId(question_id)
        for l in self.lessons:
            for r in l.resources:
                if exercise_resources._isinstance(r):
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
