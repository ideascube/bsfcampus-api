import datetime
import io
import os
from bson import json_util

from flask import Blueprint, request, jsonify, abort, Response
from MookAPI.auth import jwt_required
from flask_jwt import current_user, verify_jwt

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
    resources, \
    misc_activities, \
    visited_user_dashboards, \
    visited_resources, \
    visited_skills, \
    visited_tracks, \
    video_resources, \
    external_video_resources

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

    return attempt, 201


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


@route(bp, "/exercise_attempts/<attempt_id>/answer", methods=['POST'])
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

    if attempt.is_attempt_completed():
        attempt.end()
        if attempt.is_exercise_validated():
            attempt.is_validated = True
            attempt.save()
            achievements = current_user.add_completed_resource(attempt.exercise)
            return jsonify(
                data=attempt,
                achievements=achievements
            )
        else:
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

    return attempt, 201


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


@route(bp, "/skill_validation_attempts/<attempt_id>/answer", methods=['POST'])
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

    if attempt.is_attempt_completed():
        attempt.end()
        if attempt.is_skill_validation_validated():
            attempt.is_validated = True
            attempt.save()
            achievements = current_user.add_completed_skill(attempt.skill, True)
            return jsonify(data=attempt, achievements=achievements)
        else:
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

    return attempt, 201


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

    if attempt.is_attempt_completed():
        attempt.end()
        if attempt.is_exercise_validated():
            attempt.is_validated = True
            attempt.save()
            achievements = current_user.add_completed_track(attempt.exercise.parent)
            return jsonify(
                data=attempt,
                achievements=achievements
            )
        else:
            attempt.save()

    return attempt


## Various activity related actions

@route(bp, "/visited_dashboard", methods=['POST'])
@jwt_required()
def record_visited_user_dashboard_analytic():
    """ Creates a new VisitedDashboardActivity object which is used to track analytics on the platform
    :param user_id: the id of the user from which we want to get the dashboard
    """
    try:
        data = request.get_json()
        dashboard_user = users.get_or_404(data['dashboard_user'])
        credentials = current_user._get_current_object()
        obj = visited_user_dashboards.create(
            credentials=credentials,
            dashboard_user=dashboard_user
        )
    except Exception as e:
        return jsonify(error=e.message), 400
    else:
        return obj, 201


@route(bp, "/visited_resource", methods=['POST'])
@jwt_required()
def record_visited_resource_analytic():
    """ Creates a new VisitedDashboardActivity object which is used to track analytics on the platform
    :param user_id: the id of the user from which we want to get the dashboard
    """
    try:
        data = request.get_json()
        resource = resources.get_or_404(data['resource'])
        credentials = current_user._get_current_object()
        visited_resource, achievements = credentials.add_visited_resource(resource=resource)


    except Exception as e:
        return jsonify(error=e.message), 400
    else:
        return jsonify(
            data=visited_resource,
            achievements=achievements
        ), 201


@route(bp, "/visited_skill", methods=['POST'])
@jwt_required()
def record_visited_skill_analytic():
    """ Creates a new VisitedDashboardActivity object which is used to track analytics on the platform
    :param user_id: the id of the user from which we want to get the dashboard
    """
    try:
        data = request.get_json()
        skill = skills.get_or_404(data['skill'])
        credentials = current_user._get_current_object()
        obj = visited_skills.create(
            credentials=credentials,
            skill=skill
        )
    except Exception as e:
        return jsonify(error=e.message), 400
    else:
        return obj, 201


@route(bp, "/visited_track", methods=['POST'])
@jwt_required()
def record_visited_track_analytic():
    """ Creates a new VisitedDashboardActivity object which is used to track analytics on the platform
    :param user_id: the id of the user from which we want to get the dashboard
    """
    try:
        data = request.get_json()
        track = tracks.get_or_404(data['track'])
        credentials = current_user._get_current_object()
        obj = visited_tracks.create(
            credentials=credentials,
            track=track
        )
    except Exception as e:
        return jsonify(error=e.message), 400
    else:
        return obj, 201


@route(bp, "/watched_video", methods=['POST'])
@jwt_required()
def mark_video_resource_watched():
    """
    Set the is_validated attribute for the given video resource
    :return: the updated resource data
    """
    data = request.get_json()
    resource = resources.get_or_404(data['resource'])
    if video_resources._isinstance(resource) or external_video_resources._isinstance(resource):
        try:
            credentials = current_user._get_current_object()
            achievements = credentials.add_completed_resource(resource=resource)
        except Exception as e:
            return jsonify(error=e.message), 400
        else:
            return jsonify(
                achievements=achievements
            ), 201

    abort(404)


@route(bp, "/misc", methods=['POST'])
def record_misc_analytic():
    """ Creates a new MiscActivity object which is used to track analytics on the platform
    :param misc_type: the type of the analytic
    """

    data = request.get_json()
    obj = misc_activities.new(**data)
    try:
        verify_jwt()
    except:
        pass
    else:
        obj.credentials = current_user._get_current_object()

    try:
        obj.save()
    except Exception as e:
        return jsonify(error=e.message), 400
    else:
        return obj, 201


@route(bp, "/analytics.csv", methods=['GET'])
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
    file_path = os.path.join("/tmp", file_name)

    def write():
         analytics_writer = UnicodeCSVWriter()
         yield analytics_writer.csv_row_serialize(activities.__model__.field_names_header_for_csv())
         for activity in all_analytics:
             yield analytics_writer.csv_object_serialize(activity)

    response = Response(write())
    response.headers['Content-Disposition'] = "attachment; filename=%s"%file_name
    response.headers['Content-type'] = 'text/csv'

    return response

