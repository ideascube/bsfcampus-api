import flask
from bson import json_util
from flask_cors import cross_origin

import documents
import documents.exercise_attempt
from MookAPI.resources import documents as resources_documents
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


@bp.route("/skill_validation_attempts/<attempt_id>")
@security.login_required
def get_exercise_attempt(attempt_id):
    """GET one exercise attempt"""

    print "GETTING exercise attempt with id {attempt_id}".format(attempt_id=attempt_id)

    exercise_attempt = documents.exercise_attempt.ExerciseAttempt.objects.get_or_404(id=attempt_id)

    return flask.Response(
        response=json_util.dumps({'exercise_attempt': exercise_attempt.encode_mongo()}),
        mimetype="application/json"
    )


@bp.route("/skill_validation_attempts/<attempt_id>/answer", methods=['POST'])
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
