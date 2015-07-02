from bson import json_util

from flask import Blueprint, request, jsonify
from MookAPI.auth import jwt_required
from flask_jwt import current_user

from MookAPI.services import \
    exercise_attempts, \
    skill_validation_attempts, \
    track_validation_attempts, \
    exercise_resources, \
    track_validation_resources, \
    skills

from . import route

bp = Blueprint("activity", __name__, url_prefix="/activity")


## Exercises (as Resources) attempts

@route(bp, "/exercise_attempts", methods=['POST'])
@jwt_required()
def post_exercise_attempt():
    exercise_id = request.get_json()['exercise']
    exercise = exercise_resources.get_or_404(exercise_id)

    print "CREATING exercise attempt for exercise {exercise}".format(exercise=exercise.id)

    attempt = exercise_attempts.__model__.init_with_exercise(exercise)
    attempt.save()

    current_user._get_current_object().add_exercise_attempt(attempt)
    current_user._get_current_object().save()

    return jsonify(data=attempt)


@route(bp, "/exercise_attempts/<attempt_id>")
@jwt_required()
def get_exercise_attempt(attempt_id):
    """GET one exercise attempt"""

    print "GETTING exercise attempt with id {attempt_id}".format(attempt_id=attempt_id)

    exercise_attempt = exercise_attempts.get_or_404(attempt_id)
    
    return jsonify(data=exercise_attempt)


@route(bp, "/exercise_attempts/<attempt_id>/answer", methods=['POST'])
@jwt_required()
def post_exercise_attempt_question_answer(attempt_id):
    """POST answer to current question of an exercise attempt"""

    print "POSTING answer to current question of attempt {attempt_id}".format(attempt_id=attempt_id)

    attempt = exercise_attempts.get_or_404(attempt_id)

    form_data = json_util.loads(request.form.get('form_data'))
    question_id = form_data['question_id']
    attempt.save_answer(question_id, form_data)
    attempt.save()

    if attempt.is_exercise_completed():
        exercise_resource = attempt.exercise
        current_user._get_current_object().add_completed_resource(exercise_resource)
        current_user._get_current_object().save(validate=False)
        # FIXME We need to skip validation due to a dereferencing bug in MongoEngine.
        # It should be solved in version 0.10.1

    return jsonify(data=attempt)


## Skill Validation's attempts

@route(bp, "/skill_validation_attempts", methods=['POST'])
@jwt_required()
def post_skill_validation_attempt():
    skill_id = request.get_json()['skill']
    skill = skills.get_or_404(skill_id)

    print "CREATING skill validation attempt for skill {skill}".format(skill=skill.id)

    attempt = skill_validation_attempts.__model__.init_with_skill(skill)
    attempt.save()

    current_user._get_current_object().add_skill_validation_attempt(attempt)
    current_user._get_current_object().save()

    return jsonify(data=attempt)


@route(bp, "/skill_validation_attempts/<attempt_id>")
@jwt_required()
def get_skill_validation_attempt(attempt_id):
    """GET one skill validation attempt"""

    print "GETTING skill validation attempt with id {attempt_id}".format(attempt_id=attempt_id)

    skill_validation_attempt = skill_validation_attempts.get_or_404(id=attempt_id)

    return jsonify(data=skill_validation_attempt)


@route(bp, "/skill_validation_attempts/<attempt_id>/answer", methods=['POST'])
@jwt_required()
def post_skill_validation_attempt_question_answer(attempt_id):
    """POST answer to current question of a skill validation attempt"""

    print "POSTING answer to current question of attempt {attempt_id}".format(attempt_id=attempt_id)

    attempt = skill_validation_attempts.get_or_404(attempt_id)

    form_data = json_util.loads(request.form.get('form_data'))
    question_id = form_data['question_id']
    attempt.save_answer(question_id, form_data)
    attempt.save()

    if attempt.is_skill_validation_completed():
        skill = attempt.skill
        current_user._get_current_object().add_completed_skill(skill)
        current_user._get_current_object().save()

    return jsonify(data=attempt)


## Track Validation's attempts

@route(bp, "/track_validation_attempts", methods=['POST'])
@jwt_required()
def post_track_validation_attempt():
    exercise_id = request.get_json()['exercise']
    exercise =  track_validation_resources.get_or_404(id=exercise_id)

    print "CREATING track validation attempt for exercise {exercise}".format(exercise=exercise.id)

    attempt = track_validation_attempts.__model__.init_with_exercise(exercise)
    attempt.save()

    current_user._get_current_object().add_track_validation_attempt(attempt)
    current_user._get_current_object().save()

    return jsonify(data=attempt)


@route(bp, "/track_validation_attempts/<attempt_id>")
@jwt_required()
def get_track_validation_attempt(attempt_id):
    """GET one track validation attempt"""

    print "GETTING track validation attempt with id {attempt_id}".format(attempt_id=attempt_id)

    track_validation_attempt = track_validation_attempts.get_or_404(attempt_id)

    return jsonify(data=track_validation_attempt)


@route(bp, "/track_validation_attempts/<attempt_id>/answer", methods=['POST'])
@jwt_required()
def post_track_validation_attempt_question_answer(attempt_id):
    """POST answer to current question of a track validation attempt"""

    print "POSTING answer to current question of attempt {attempt_id}".format(attempt_id=attempt_id)

    attempt = track_validation_attempts.get_or_404(id=attempt_id)

    form_data = json_util.loads(request.form.get('form_data'))
    question_id = form_data['question_id']
    attempt.save_answer(question_id, form_data)
    attempt.save()

    if attempt.is_exercise_completed():
        track = attempt.exercise.parent
        current_user._get_current_object().add_completed_track(track)
        current_user._get_current_object().save()

    return jsonify(data=attempt)
