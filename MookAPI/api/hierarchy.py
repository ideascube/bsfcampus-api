import io

from flask import Blueprint, jsonify, send_file, abort
from flask_jwt import current_user, verify_jwt

from MookAPI.auth import jwt_required
from MookAPI.services import tracks, skills, lessons, misc_activities
import activity

from . import route

bp = Blueprint("hierarchy", __name__, url_prefix="/hierarchy")

### OVERALL HIERARCHY

@route(bp, "")
def get_overall_hierarchy_skeleton():
    """
    Get the most concise list of all the objects related to resources and their hierarchy
    :return: a JSON object with all tracks, with their skills, lessons and resources
    """

    rv = map(lambda t: t.to_json_hierarchy_skeleton(), tracks.all())
    return jsonify(data=rv)


### TRACKS

@route(bp, "/tracks")
@jwt_required()
def get_tracks():
    """Get the list of all Track_ objects, ordered by ``order`` and ``title``, enveloped in a single-key JSON dictionary."""

    return tracks.all().order_by('order', 'title')

@route(bp, "/tracks/<track_id>")
# @jwt_required()
def get_track(track_id):
    """Get the Track_ with id ``track_id`` enveloped in a single-key JSON dictionary."""
    track = tracks.get_or_404(track_id)

    try:
        verify_jwt()
    except:
        pass

    return track

@route(bp, "/tracks/<track_id>/icon")
# @jwt_required()
def get_track_icon(track_id):
    """Download the icon of the Track_ with id ``track_id``."""

    track = tracks.get_or_404(track_id)
    return send_file(
            io.BytesIO(track.icon.read()),
            attachment_filename=track.icon.filename,
            mimetype=track.icon.contentType
        )


### SKILLS

@route(bp, "/skills")
@jwt_required()
def get_skills():
    """Returns a list of all Skill_ objects, ordered by ``order`` and ``title``, enveloped in a single-key JSON dictionary."""

    return skills.all().order_by('order', 'title')

@route(bp, "/skills/track/<track_id>")
@jwt_required()
def get_track_skills(track_id):
    """Returns a list of all Skill_ objects in a Track_, ordered by ``order`` and ``title``, enveloped in a single-key JSON dictionary."""

    return skills.find(track=track_id).order_by('order', 'title')

@route(bp, "/skills/<skill_id>")
# @jwt_required()
def get_skill(skill_id):
    """Get the Skill_ with id ``skill_id`` enveloped in a single-key JSON dictionary."""

    skill = skills.get_or_404(skill_id)

    try:
        verify_jwt()
    except:
        pass

    return skill

@route(bp, "/skills/<skill_id>/icon")
# @jwt_required()
def get_skill_icon(skill_id):
    """Download the icon of the Skill_ with id ``skill_id``."""

    skill = skills.get_or_404(skill_id)
    if not skill.icon:
        abort(404)
    return send_file(
            io.BytesIO(skill.icon.read()),
            attachment_filename=skill.icon.filename,
            mimetype=skill.icon.contentType
        )


### LESSONS

@route(bp, "/lessons")
@jwt_required()
def get_lessons():
    """Returns a list of all Lesson_ objects, ordered by ``order`` and ``title``, enveloped in a single-key JSON dictionary."""

    return lessons.all().order_by('order', 'title')

@route(bp, "/lessons/skill/<skill_id>")
@jwt_required()
def get_skill_lessons(skill_id):
    """Returns a list of all Lesson_ objects in a Skill_, ordered by ``order`` and ``title``, enveloped in a single-key JSON dictionary."""

    return lessons.find(skill=skill_id).order_by('order', 'title')

@route(bp, "/lessons/<lesson_id>")
# @jwt_required()
def get_lesson(lesson_id):
    """Get the Lesson_ with id ``lesson_id`` enveloped in a single-key JSON dictionary."""

    return lessons.get_or_404(lesson_id)
