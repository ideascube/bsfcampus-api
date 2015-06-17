import flask
from bson import json_util
from flask_cors import cross_origin

import documents
import documents.exercise_attempt
import documents.skill_validation_attempt
import documents.track_validation_attempt
from MookAPI.resources import documents as resources_documents
from MookAPI.hierarchy import documents as hierarchy_documents
import flask.ext.security as security
from . import bp

## Exercises (as Resources) attempts

@bp.route("/exercise_attempts", methods=['POST'])
@security.login_required
def post_exercise_attempt():
    exercise_id = flask.request.get_json()['exercise']
    exercise = resources_documents.Resource.objects.get_or_404(id=exercise_id)

    print "CREATING exercise attempt for exercise {exercise}".format(exercise=exercise.id)

    attempt = documents.exercise_attempt.ExerciseAttempt.init_with_exercise(exercise)
    attempt.save()

    security.current_user.add_exercise_attempt(attempt)

    return flask.Response(
        response=json_util.dumps({'exercise_attempt': attempt.encode_mongo()}),
        mimetype="application/json"
    )


@bp.route("/exercise_attempts/<attempt_id>")
@security.login_required
def get_exercise_attempt(attempt_id):
    """GET one exercise attempt"""

    print "GETTING exercise attempt with id {attempt_id}".format(attempt_id=attempt_id)

    exercise_attempt = documents.exercise_attempt.ExerciseAttempt.objects.get_or_404(id=attempt_id)
    
    return flask.Response(
        response=json_util.dumps({'exercise_attempt': exercise_attempt.encode_mongo()}),
        mimetype="application/json"
    )


@bp.route("/exercise_attempts/<attempt_id>/answer", methods=['POST'])
@security.login_required
def post_exercise_attempt_question_answer(attempt_id):
    """POST answer to current question of an exercise attempt"""

    print "POSTING answer to current question of attempt {attempt_id}".format(attempt_id=attempt_id)

    attempt = documents.exercise_attempt.ExerciseAttempt.objects.get_or_404(id=attempt_id)

    form_data = json_util.loads(flask.request.form.get('form_data'))
    question_id = form_data['question_id']
    attempt.save_answer(question_id, form_data)
    attempt.save()

    if attempt.is_exercise_completed():
        exercise_resource = attempt.exercise
        security.current_user.add_completed_resource(exercise_resource)

    return flask.Response(
        response=json_util.dumps({'exercise_attempt': attempt.encode_mongo()}),
        mimetype="application/json"
    )


## Skill Validation's attempts

@bp.route("/skill_validation_attempts", methods=['POST'])
@security.login_required
def post_skill_validation_attempt():
    skill_id = flask.request.get_json()['skill']
    skill = hierarchy_documents.skill.Skill.objects.get_or_404(id=skill_id)

    print "CREATING skill validation attempt for skill {skill}".format(skill=skill.id)

    attempt = documents.skill_validation_attempt.SkillValidationAttempt.init_with_skill(skill)
    attempt.save()

    security.current_user.add_skill_validation_attempt(attempt)

    return flask.Response(
        response=json_util.dumps({'skill_validation_attempt': attempt.encode_mongo()}),
        mimetype="application/json"
    )


@bp.route("/skill_validation_attempts/<attempt_id>")
@security.login_required
def get_skill_validation_attempt(attempt_id):
    """GET one skill validation attempt"""

    print "GETTING skill validation attempt with id {attempt_id}".format(attempt_id=attempt_id)

    skill_validation_attempt = documents.skill_validation_attempt.SkillValidationAttempt.objects.get_or_404(id=attempt_id)

    return flask.Response(
        response=json_util.dumps({'skill_validation_attempt': skill_validation_attempt.encode_mongo()}),
        mimetype="application/json"
    )


@bp.route("/skill_validation_attempts/<attempt_id>/answer", methods=['POST'])
@security.login_required
def post_skill_validation_attempt_question_answer(attempt_id):
    """POST answer to current question of a skill validation attempt"""

    print "POSTING answer to current question of attempt {attempt_id}".format(attempt_id=attempt_id)

    attempt = documents.skill_validation_attempt.SkillValidationAttempt.objects.get_or_404(id=attempt_id)

    form_data = json_util.loads(flask.request.form.get('form_data'))
    question_id = form_data['question_id']
    attempt.save_answer(question_id, form_data)
    attempt.save()

    if attempt.is_skill_validation_completed():
        skill = attempt.skill
        security.current_user.add_completed_skill(skill)

    return flask.Response(
        response=json_util.dumps({'skill_validation_attempt': attempt.encode_mongo()}),
        mimetype="application/json"
    )


## Track Validation's attempts

@bp.route("/track_validation_attempts", methods=['POST'])
@security.login_required
def post_track_validation_attempt():
    exercise_id = flask.request.get_json()['exercise']
    exercise = resources_documents.Resource.objects.get_or_404(id=exercise_id)

    print "CREATING track validation attempt for exercise {exercise}".format(exercise=exercise.id)

    attempt = documents.track_validation_attempt.TrackValidationAttempt.init_with_exercise(exercise)
    attempt.save()

    security.current_user.add_exercise_attempt(attempt)

    return flask.Response(
        response=json_util.dumps({'track_validation_attempt': attempt.encode_mongo()}),
        mimetype="application/json"
    )


@bp.route("/track_validation_attempts/<attempt_id>")
@security.login_required
def get_track_validation_attempt(attempt_id):
    """GET one track validation attempt"""

    print "GETTING track validation attempt with id {attempt_id}".format(attempt_id=attempt_id)

    track_validation_attempt = documents.track_validation_attempt.TrackValidationAttempt.objects.get_or_404(id=attempt_id)

    return flask.Response(
        response=json_util.dumps({'track_validation_attempt': track_validation_attempt.encode_mongo()}),
        mimetype="application/json"
    )


@bp.route("/track_validation_attempts/<attempt_id>/answer", methods=['POST'])
@security.login_required
def post_track_validation_attempt_question_answer(attempt_id):
    """POST answer to current question of a track validation attempt"""

    print "POSTING answer to current question of attempt {attempt_id}".format(attempt_id=attempt_id)

    attempt = documents.track_validation_attempt.TrackValidationAttempt.objects.get_or_404(id=attempt_id)

    form_data = json_util.loads(flask.request.form.get('form_data'))
    question_id = form_data['question_id']
    attempt.save_answer(question_id, form_data)
    attempt.save()

    if attempt.is_exercise_completed():
        track = attempt.exercise.parent
        security.current_user.add_completed_track(track)

    return flask.Response(
        response=json_util.dumps({'track_validation_attempt': attempt.encode_mongo()}),
        mimetype="application/json"
    )
