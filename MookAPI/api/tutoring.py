from flask import Blueprint
from flask_jwt import current_user

from MookAPI.services import users
from MookAPI.auth import jwt_required

from . import route

bp = Blueprint('tutoring', __name__, url_prefix="/tutoring")


@route(bp, "/request/tutor/<user_id>", methods=['POST'])
@jwt_required()
def post_tutor_request(user_id):
    requested_tutor = users.get_or_404(user_id)

    current_user_object = current_user._get_current_object()
    if requested_tutor in current_user_object.tutors:
        response = {"error_code": 1, "error_message": "The requested user is already a tutor for you"}
    elif requested_tutor in current_user_object.tutored_students:
        response = {"error_code": 2, "error_message": "The requested user is already tutored by you"}
    elif current_user_object in requested_tutor.awaiting_tutor_requests:
        response = {"error_code": 3, "error_message": "A tutor request is already registered for this user"}
    elif current_user_object in requested_tutor.awaiting_student_requests:
        response = {"error_code": 4, "error_message": "A tutoring request is already registered for this user"}
    else:
        requested_tutor.awaiting_tutor_requests.append(current_user_object)
        requested_tutor.save()
        response = {"error_code": 0}

    return response


@route(bp, "/request/student/<user_id>", methods=['POST'])
@jwt_required()
def post_tutored_student_request(user_id):
    requested_student = users.get_or_404(user_id)

    current_user_object = current_user._get_current_object()
    if requested_student in current_user_object.tutored_students:
        response = {"error_code": 5, "error_message": "The requested user is already tutored by you"}
    elif requested_student in current_user_object.tutors:
        response = {"error_code": 6, "error_message": "The requested user is already a tutor for you"}
    elif current_user_object in requested_student.awaiting_tutor_requests:
        response = {"error_code": 7, "error_message": "A tutor request is already registered for this user"}
    elif current_user_object in requested_student.awaiting_student_requests:
        response = {"error_code": 8, "error_message": "A tutoring request is already registered for this user"}
    else:
        requested_student.awaiting_student_requests.append(current_user_object)
        requested_student.save()
        response = {"error_code": 0}

    return response


@route(bp, "/accept/tutor/<user_id>", methods=['POST'])
@jwt_required()
def post_tutor_accept(user_id):
    requesting_student = users.get_or_404(user_id)

    current_user_object = current_user._get_current_object()
    if requesting_student not in current_user_object.awaiting_tutor_requests:
        response = {"error_code": 9, "error_message": "There is no request to respond for this user"}
    else:
        current_user_object.awaiting_tutor_requests.remove(current_user_object)
        current_user_object.tutored_students.append(requesting_student)
        current_user_object.save()
        requesting_student.tutors.append(current_user_object)
        requesting_student.save()
        response = {"error_code": 0}

    return response


@route(bp, "/decline/tutor/<user_id>", methods=['POST'])
@jwt_required()
def post_tutor_decline(user_id):
    requesting_student = users.get_or_404(user_id)

    current_user_object = current_user._get_current_object()
    if requesting_student not in current_user_object.awaiting_tutor_requests:
        response = {"error_code": 9, "error_message": "There is no request to respond for this user"}
    else:
        current_user_object.awaiting_tutor_requests.remove(current_user_object)
        current_user_object.save()
        response = {"error_code": 0}

    return response


@route(bp, "/accept/student/<user_id>", methods=['POST'])
@jwt_required()
def post_tutored_student_accept(user_id):
    requesting_tutor = users.get_or_404(user_id)

    current_user_object = current_user._get_current_object()
    if requesting_tutor not in current_user_object.awaiting_student_requests:
        response = {"error_code": 9, "error_message": "There is no request to respond for this user"}
    else:
        current_user_object.awaiting_student_requests.remove(current_user_object)
        current_user_object.tutors.append(requesting_tutor)
        current_user_object.save()
        requesting_tutor.tutored_students.append(current_user_object)
        requesting_tutor.save()
        response = {"error_code": 0}

    return response


@route(bp, "/decline/student/<user_id>", methods=['POST'])
@jwt_required()
def post_tutored_student_decline(user_id):
    requesting_tutor = users.get_or_404(user_id)

    current_user_object = current_user._get_current_object()
    if requesting_tutor not in current_user_object.awaiting_student_requests:
        response = {"error_code": 9, "error_message": "There is no request to respond for this user"}
    else:
        current_user_object.awaiting_student_requests.remove(current_user_object)
        current_user_object.save()
        response = {"error_code": 0}

    return response


@route(bp, "/cancel/<user_id>", methods=['POST'])
@jwt_required()
def post_cancel_request(user_id):
    other_user = users.get_or_404(user_id)

    current_user_object = current_user._get_current_object()
    if current_user_object not in other_user.awaiting_student_requests and current_user_object not in other_user.awaiting_tutor_requests:
        response = {"error_code": 10, "error_message": "There is no request to cancel for this user"}
    else:
        other_user.awaiting_student_requests.remove(current_user_object)
        other_user.awaiting_tutor_requests.remove(current_user_object)
        other_user.save()
        response = {"error_code": 0}

    return response


@route(bp, "/remove/<user_id>", methods=['POST'])
@jwt_required()
def post_remove_relationship(user_id):
    other_user = users.get_or_404(user_id)

    current_user_object = current_user._get_current_object()
    other_user.tutors.remove(current_user_object)
    other_user.tutored_students.remove(current_user_object)
    other_user.save()
    current_user_object.tutors.remove(other_user)
    current_user_object.tutored_students.remove(other_user)
    current_user_object.save()
    response = {"error_code": 0}

    return response
