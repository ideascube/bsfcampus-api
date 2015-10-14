import io

from flask import Blueprint, jsonify, send_file, abort
from flask_jwt import current_user, verify_jwt
from MookAPI.auth import jwt_required

from MookAPI.services import \
    resources, \
    lessons, \
    exercise_resources, \
    downloadable_file_resources, \
    audio_resources, \
    linked_file_resources

from MookAPI.helpers import send_file_partial

from . import route

bp = Blueprint('resources', __name__, url_prefix="/resources")


@route(bp, "/")
@jwt_required()
def get_resources():
    return resources.find(is_published__ne=False).order_by('parent', 'order', 'title')


@route(bp, "/lesson/<lesson_id>")
@jwt_required()
def get_lesson_resources(lesson_id):
    return resources.find(is_published__ne=False,parent=lesson_id).order_by('order', 'title')


@route(bp, "/skill/<skill_id>")
@jwt_required()
def get_skill_resources(skill_id):
    lessons_list = lessons.find(is_published__ne=False,skill=skill_id)
    return resources.find(is_published__ne=False,parent__in=lessons_list).order_by('order', 'title')


@route(bp, "/<resource_id>")
# @jwt_required()
def get_resource(resource_id):

    # FIXME We need to find out what the best place is to alert that the track validation test is available
    # This is how it was done before:
    # if current_user.user.is_track_test_available_and_never_attempted(resource.track):
    #     alert = {"code": "prompt_track_validation", "id": resource.track._data.get("id", None)}
    #     return jsonify(data=resource, alert=alert)

    return resources.get_or_404(is_published__ne=False,id=resource_id)

@route(bp, "/<resource_id>/hierarchy")
@jwt_required()
def get_resource_hierarchy(resource_id):
    resource = resources.get_or_404(resource_id)

    lesson = resource.parent
    skill = lesson.skill
    track = skill.track

    return jsonify(
        data=resource,
        lesson=lesson,
        skill=skill,
        track=track,
        siblings=resource.siblings(),
        aunts=resource.aunts(),
        cousins=resource.cousins()
    )

@route(bp, "/<resource_id>/content-image/<filename>")
# @jwt_required()
def get_resource_content_image(resource_id, filename):
    resource = resources.get_or_404(is_published__ne=False,id=resource_id)

    if audio_resources._isinstance(resource):
        content_image = resource.resource_content.image

        return send_file(
            io.BytesIO(content_image.read()),
            attachment_filename=content_image.filename,
            mimetype=content_image.contentType
        )

    abort(404)


@route(bp, "/<resource_id>/question/<question_id>/image/<filename>")
# @jwt_required()
def get_exercise_question_image(resource_id, question_id, filename):
    resource = exercise_resources.get_or_404(is_published__ne=False,id=resource_id)

    try:
        question = resource.question(question_id=question_id)
        question_image = question.question_image
        return send_file(
            io.BytesIO(question_image.read()),
            attachment_filename=question_image.filename,
            mimetype=question_image.contentType
        )
    except:
        abort(404)
