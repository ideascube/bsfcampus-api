import datetime
import io
from bson import json_util

from flask import Blueprint, request, send_file, jsonify, abort
from MookAPI.auth import jwt_required
from flask_jwt import current_user

from MookAPI.services import \
    activities, \
    exercise_attempts, \
    skill_validation_attempts, \
    track_validation_attempts, \
    exercise_resources, \
    track_validation_resources, \
    skills, \
    tracks, \
    users, \
    resources

from MookAPI.serialization import UnicodeCSVWriter

from . import route

bp = Blueprint("activity", __name__, url_prefix="/activity")


@route(bp, "/<activity_id>")
def get_activity(activity_id):
    return activities.get_or_404(activity_id)


## Exercises (as Resources) attempts

@route(bp, "/exercise_attempts", methods=['POST'])
@jwt_required()
def post_exercise_attempt():
    exercise_id = request.get_json()['exercise']
    exercise = exercise_resources.get_or_404(exercise_id)

    attempt = exercise_attempts.__model__.init_with_exercise(exercise)
    attempt.credentials = current_user._get_current_object()
    attempt.save()

    return attempt


@route(bp, "/exercise_attempts/<attempt_id>")
@jwt_required()
def get_exercise_attempt(attempt_id):
    """GET one exercise attempt"""

    attempt = exercise_attempts.get_or_404(attempt_id)
    if attempt.user != current_user.user:
        abort(403)
    return attempt


@route(bp, "/exercise_attempts/<attempt_id>/start_next_question", methods=['POST'])
@jwt_required()
def start_exercise_attempt_next_question(attempt_id):
    """ records the fact that the user has started the next question """

    attempt = exercise_attempts.get_or_404(attempt_id)
    if attempt.user != current_user.user:
        abort(403)

    form_data = json_util.loads(request.form.get('form_data'))
    question_id = form_data['question_id']
    attempt.start_question(question_id)
    attempt.save()

    return attempt


@route(bp, "/exercise_attempts/<attempt_id>/answer", methods=['POST'], jsonify_wrap=False)
@jwt_required()
def post_exercise_attempt_question_answer(attempt_id):
    """POST answer to current question of an exercise attempt"""

    attempt = exercise_attempts.get_or_404(attempt_id)
    if attempt.user != current_user.user:
        abort(403)

    form_data = json_util.loads(request.form.get('form_data'))
    question_id = form_data['question_id']
    attempt.save_answer(question_id, form_data)
    attempt.save()

    response = jsonify(data=attempt)
    if attempt.is_exercise_completed():
        attempt.is_validated = True
        exercise_resource = attempt.exercise
        current_user.add_completed_resource(exercise_resource)
        if current_user.user.is_track_test_available_and_never_attempted(attempt.exercise.track):
            alert = {"code": "prompt_track_validation", "id": attempt.exercise.track._data.get("id", None)}
            response = jsonify(data=attempt, alert=alert)

    return response


@route(bp, "/exercise_attempts/<attempt_id>/end", methods=['POST'])
@jwt_required()
def end_exercise_attempt(attempt_id):
    """ records the date and time when the user has finished (failed or succeeded) the attempt """

    attempt = exercise_attempts.get_or_404(attempt_id)
    if attempt.user != current_user.user:
        abort(403)

    attempt.end()
    attempt.save()

    return attempt


## Skill Validation's attempts

@route(bp, "/skill_validation_attempts", methods=['POST'])
@jwt_required()
def post_skill_validation_attempt():
    skill_id = request.get_json()['skill']
    skill = skills.get_or_404(skill_id)

    print "CREATING skill validation attempt for skill {skill}".format(skill=skill.id)

    attempt = skill_validation_attempts.__model__.init_with_skill(skill)
    attempt.credentials = current_user._get_current_object()
    attempt.save()

    return attempt


@route(bp, "/skill_validation_attempts/<attempt_id>")
@jwt_required()
def get_skill_validation_attempt(attempt_id):
    """GET one skill validation attempt"""

    # FIXME Check that attempt.user == current_user
    return skill_validation_attempts.get_or_404(id=attempt_id)


@route(bp, "/skill_validation_attempts/<attempt_id>/start_next_question", methods=['POST'])
@jwt_required()
def start_skill_validation_attempt_next_question(attempt_id):
    """ records the fact that the user has started the next question """

    attempt = skill_validation_attempts.get_or_404(attempt_id)
    if attempt.user != current_user.user:
        abort(403)

    form_data = json_util.loads(request.form.get('form_data'))
    question_id = form_data['question_id']
    attempt.start_question(question_id)
    attempt.save()

    return attempt


@route(bp, "/skill_validation_attempts/<attempt_id>/answer", methods=['POST'], jsonify_wrap=False)
@jwt_required()
def post_skill_validation_attempt_question_answer(attempt_id):
    """POST answer to current question of a skill validation attempt"""

    attempt = skill_validation_attempts.get_or_404(attempt_id)
    if attempt.user != current_user.user:
        abort(403)

    form_data = json_util.loads(request.form.get('form_data'))
    question_id = form_data['question_id']
    attempt.save_answer(question_id, form_data)
    attempt.save()

    response = jsonify(data=attempt)

    if attempt.is_skill_validation_completed():
        attempt.is_validated = True
        skill = attempt.skill
        current_user.add_completed_skill(skill, True)
        if current_user.user.is_track_test_available_and_never_attempted(skill.track):
            alert = {"code": "prompt_track_validation", "id": skill.track._data.get("id", None)}
            response = jsonify(data=attempt, alert=alert)

    return response


@route(bp, "/skill_validation_attempts/<attempt_id>/end", methods=['POST'])
@jwt_required()
def end_skill_validation_attempt(attempt_id):
    """ records the date and time when the user has finished (failed or succeeded) the attempt """

    attempt = skill_validation_attempts.get_or_404(attempt_id)
    if attempt.user != current_user.user:
        abort(403)

    attempt.end()
    attempt.save()

    return attempt


## Track Validation's attempts

@route(bp, "/track_validation_attempts", methods=['POST'])
@jwt_required()
def post_track_validation_attempt():
    exercise_id = request.get_json()['exercise']
    exercise = track_validation_resources.get_or_404(id=exercise_id)

    attempt = track_validation_attempts.__model__.init_with_exercise(exercise)
    attempt.credentials = current_user._get_current_object()
    attempt.save()

    return attempt


@route(bp, "/track_validation_attempts/<attempt_id>")
@jwt_required()
def get_track_validation_attempt(attempt_id):
    """GET one track validation attempt"""

    attempt = track_validation_attempts.get_or_404(attempt_id)
    if attempt.user != current_user.user:
        abort(403)
    return attempt


@route(bp, "/track_validation_attempts/<attempt_id>/start_next_question", methods=['POST'])
@jwt_required()
def start_track_validation_attempt_next_question(attempt_id):
    """ records the fact that the user has started the next question """

    attempt = track_validation_attempts.get_or_404(attempt_id)
    if attempt.user != current_user.user:
        abort(403)

    form_data = json_util.loads(request.form.get('form_data'))
    question_id = form_data['question_id']
    attempt.start_question(question_id)
    attempt.save()

    return attempt


@route(bp, "/track_validation_attempts/<attempt_id>/answer", methods=['POST'])
@jwt_required()
def post_track_validation_attempt_question_answer(attempt_id):
    """POST answer to current question of a track validation attempt"""

    attempt = track_validation_attempts.get_or_404(id=attempt_id)

    form_data = json_util.loads(request.form.get('form_data'))
    question_id = form_data['question_id']
    attempt.save_answer(question_id, form_data)
    attempt.save()

    if attempt.is_exercise_completed():
        attempt.is_validated = True
        track = attempt.exercise.parent
        current_user.add_completed_track(track)

    return attempt


@route(bp, "/track_validation_attempts/<attempt_id>/end", methods=['POST'])
@jwt_required()
def end_track_validation_attempt(attempt_id):
    """ records the date and time when the user has finished (failed or succeeded) the attempt """

    attempt = track_validation_attempts.get_or_404(attempt_id)
    if attempt.user != current_user.user:
        abort(403)

    attempt.end()
    attempt.save()

    return attempt


## Various activity related actions

@route(bp, "/visited_dashboard/<user_id>", methods=['POST'])
@jwt_required()
def record_visited_user_dashboard_analytic(user_id):
    """ Creates a new VisitedDashboardActivity object which is used to track analytics on the platform
    :param user_id: the id of the user from which we want to get the dashboard
    """
    requested_user = users.get_or_404(user_id)
    from MookAPI.services import visited_user_dashboards
    user = current_user.user
    return visited_user_dashboards.create(user=user, dashboard_user=requested_user)


@route(bp, "/visited_resource/<resource_id>", methods=['POST'])
@jwt_required()
def record_visited_resource_analytic(resource_id):
    resource = resources.get_or_404(resource_id)
    from MookAPI.services import visited_resources
    return visited_resources.create(
        credentials=current_user._get_current_object(),
        resource=resource
    )


@route(bp, "/visited_skill/<skill_id>", methods=['POST'])
@jwt_required()
def record_visited_skill_analytic(skill_id):
    skill = skills.get_or_404(skill_id)
    user = current_user.user
    from MookAPI.services import visited_skills
    return visited_skills.create(user=user, skill=skill)


@route(bp, "/visited_track/<track_id>", methods=['POST'])
@jwt_required()
def record_visited_track_analytic(track_id):
    track = tracks.get_or_404(track_id)
    user = current_user.user
    from MookAPI.services import visited_tracks
    return visited_tracks.create(user=user, track=track)


@route(bp, "/misc_analytics/<misc_type>", methods=['POST'])
def record_simple_misc_analytic(misc_type):
    """ Creates a new MiscActivity object which is used to track analytics on the platform
    :param misc_type: the type of the analytic
    """

    from MookAPI.services import misc_activities

    return misc_activities.create(
        credentials=current_user._get_current_object(),
        type=misc_type,
        object_title=""
    )


@route(bp, "/misc_analytics/<misc_type>/<misc_title>", methods=['POST'])
def record_misc_analytic(misc_type, misc_title):
    """ Creates a new MiscActivity object which is used to track analytics on the platform
    :param misc_type: the type of the analytic
    :param misc_title: the title of the analytic (to further differentiate misc analytics of the same type)
    """

    from MookAPI.services import misc_activities

    return misc_activities.create(
        credentials=current_user._get_current_object(),
        type=misc_type,
        object_title=misc_title
    )


@route(bp, "/analytics.csv", methods=['GET'], jsonify_wrap=False)
def get_general_analytics():
    """
    Returns a .csv file with all the activities which took place between the start_date and the end_date
    """

    start_date_arg = request.args.get('start_date', None)
    if start_date_arg is None:
        start_date = datetime.datetime.fromtimestamp(0)
    else:
        start_date = datetime.datetime.strptime(start_date_arg, "%Y-%m-%d").date()

    end_date_arg = request.args.get('end_date', None)
    if end_date_arg is None:
        end_date = datetime.datetime.now
    else:
        end_date = datetime.datetime.strptime(end_date_arg, "%Y-%m-%d").date() + datetime.timedelta(days=1)

    all_analytics = activities.__model__.objects(date__gte=start_date)(date__lte=end_date)

    file_name = "analytics_"
    file_name += start_date_arg + "_" + end_date_arg
    file_name += ".csv"
    csv_file = open(file_name, 'wb')
    analytics_writer = UnicodeCSVWriter(csv_file)
    analytics_writer.writerow(activities.__model__.field_names_header_for_csv())
    for activity in all_analytics:
        analytics_writer.writeactivity(activity)
    csv_file.close()
    csv_file = open(file_name, 'rb')
    file_bytes = io.BytesIO(csv_file.read())
    csv_file.close()

    return send_file(
        file_bytes,
        attachment_filename=file_name,
        mimetype='text/csv'
    )
