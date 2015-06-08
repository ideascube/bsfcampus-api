import io

import flask
from flask.ext import restful
from flask.ext.security import login_required
import flask.ext.security as security

from MookAPI import api
import documents
import MookAPI.hierarchy.documents


class ResourcesView(restful.Resource):

    def _get_all(self):
        return documents.Resource.objects.order_by('lesson', 'order', 'title').all()
    
    def _get_by_lesson(self, lesson_id):
        return documents.Resource.objects.order_by('order', 'title').filter(lesson=lesson_id)
    
    def _get_by_skill(self, skill_id):
        lessons = MookAPI.hierarchy.documents.Lesson.objects.filter(skill=skill_id)
        return documents.Resource.objects.order_by('lesson', 'order', 'title').filter(lesson__in=lessons)

    @login_required
    def get(self, lesson_id=None, skill_id=None):
        """
        Returns a list of Resource_ objects, ordered by ``order`` and ``title``, enveloped in a single-key JSON dictionary.
        The results are filtered by Lesson_ if ``lesson_id`` is specified or by Skill_ if ``skill_id`` is specified.
        """

        if lesson_id:
            return self._get_by_lesson(lesson_id)
        elif skill_id:
            return self._get_by_skill(skill_id)
        else:
            return self._get_all()

api.add_resource(
    ResourcesView,
    '/resources', '/resources/lesson/<lesson_id>', '/resources/skill/<skill_id>', 
    endpoint='resources'
)


class ResourceView(restful.Resource):

    @login_required
    def get(self, resource_id):
        """Get the Resource_ with id ``resource_id`` enveloped in a single-key JSON dictionary."""

        resource = documents.Resource.get_unique_object_or_404(resource_id)
        security.current_user.add_started_track(resource.lesson.skill.track)
        if not isinstance(resource, documents.exercise.ExerciseResource):
            security.current_user.add_completed_resource(resource)
        return resource

api.add_resource(ResourceView, '/resources/<resource_id>', endpoint='resource')


class ResourceHierarchyView(restful.Resource):

    @login_required
    def get(self, resource_id):
        """
        Get the Resource_ with id ``resource_id`` and all its family tree:
        Lesson_, Skill_, Track_, sibling Resource_ objects, aunt Lesson_ objects and cousin Resource_ objects.
        """

        resource = documents.Resource.get_unique_object_or_404(resource_id)

        lesson = resource.lesson
        skill = lesson.skill
        track = skill.track

        son = {}
        son[documents.Resource.json_key()] = resource.encode_mongo()
        son['lesson'] = lesson.encode_mongo()
        son['skill'] = skill.encode_mongo()
        son['track'] = track.encode_mongo()
        son['siblings'] = map(lambda r: r.encode_mongo(), resource.siblings())
        son['aunts'] = map(lambda r: r.encode_mongo(), resource.aunts())
        son['cousins'] = map(lambda r: r.encode_mongo(), resource.cousins())

        return son

api.add_resource(ResourceHierarchyView, '/resources/<resource_id>/hierarchy', endpoint='resource_hierarchy')


class ResourceContentFileView(restful.Resource):

    @login_required
    def get(self, resource_id, filename):
        """Download the file associated with the Resource_ with id ``resource_id``."""

        resource = documents.Resource.get_unique_object_or_404(resource_id)

        if isinstance(resource, documents.downloadable_file.DownloadableFileResource):
            content_file = resource.resource_content.content_file

            return flask.send_file(
                io.BytesIO(content_file.read()),
                attachment_filename=content_file.filename,
                mimetype=content_file.contentType
            )

        flask.abort(404)

api.add_resource(ResourceContentFileView, '/resources/<resource_id>/content-file/<filename>', endpoint='resource_content_file')


class ResourceContentImageView(restful.Resource):

    @login_required
    def get(self, resource_id, filename):
        """Download the image associated with the Resource_ with id ``resource_id``."""

        resource = documents.Resource.get_unique_object_or_404(resource_id)

        if isinstance(resource, documents.audio.AudioResource):
            content_image = resource.resource_content.image

            return flask.send_file(
                io.BytesIO(content_image.read()),
                attachment_filename=content_image.filename,
                mimetype=content_image.contentType
            )

        flask.abort(404)

api.add_resource(ResourceContentImageView, '/resources/<resource_id>/content-image/<filename>', endpoint='resource_content_image')


class ExerciseResourceQuestionImageView(restful.Resource):

    @login_required
    def get(self, resource_id, question_id, filename):
        """Download the image associated with the question with ``question_id`` in Exercise Resource_ with id ``resource_id``."""

        resource = documents.Resource.get_unique_object_or_404(resource_id)
        try:
            question = resource.question(question_id=question_id)
            question_image = question.question_image
            return flask.send_file(
                io.BytesIO(question_image.read()),
                attachment_filename=question_image.filename,
                mimetype=question_image.contentType
            )
        except:
            flask.abort(404)

api.add_resource(ExerciseResourceQuestionImageView, '/resources/<resource_id>/question/<question_id>/image/<filename>', endpoint='exercise_question_image')