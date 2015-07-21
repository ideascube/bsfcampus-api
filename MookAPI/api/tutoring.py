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

    user = current_user.user
    error_code = 400
    if requested_tutor in user.tutors:
        response = {"error_code": 1, "error_message": "The requested user is already a tutor for you"}
    # It should be allowed to be both student and tutor to the same user
    # elif requested_tutor in user.tutored_students:
    #     response = {"error_code": 2, "error_message": "The requested user is already tutored by you"}
    elif user in requested_tutor.awaiting_tutor_requests:
        response = {"error_code": 3, "error_message": "A tutor request is already registered for this user"}
    # It should be allowed to be both student and tutor to the same user
    # elif user in requested_tutor.awaiting_student_requests:
    #     response = {"error_code": 4, "error_message": "A tutoring request is already registered for this user"}
    else:
        requested_tutor.awaiting_tutor_requests.append(user)
        requested_tutor.save()
        response = user
        error_code = 200

    return response, error_code


@route(bp, "/request/student/<user_id>", methods=['POST'])
@jwt_required()
def post_tutored_student_request(user_id):
    requested_student = users.get_or_404(user_id)

    user = current_user.user
    error_code = 400
    if requested_student in user.tutored_students:
        response = {"error_code": 5, "error_message": "The requested user is already tutored by you"}
    # It should be allowed to be both student and tutor to the same user
    # elif requested_student in user.tutors:
    #     response = {"error_code": 6, "error_message": "The requested user is already a tutor for you"}
    # It should be allowed to be both student and tutor to the same user
    # elif user in requested_student.awaiting_tutor_requests:
    #     response = {"error_code": 7, "error_message": "A tutor request is already registered for this user"}
    elif user in requested_student.awaiting_student_requests:
        response = {"error_code": 8, "error_message": "A tutoring request is already registered for this user"}
    else:
        requested_student.awaiting_student_requests.append(user)
        requested_student.save()
        response = user
        error_code = 200

    return response, error_code


@route(bp, "/accept/tutor/<user_id>", methods=['POST'])
@jwt_required()
def post_tutor_accept(user_id):
    requesting_student = users.get_or_404(user_id)

    user = current_user.user
    error_code = 400
    if requesting_student not in user.awaiting_tutor_requests:
        response = {"error_code": 9, "error_message": "There is no request to respond for this user"}
    else:
        user.awaiting_tutor_requests.remove(requesting_student)
        user.tutored_students.append(requesting_student)
        user.save()
        requesting_student.tutors.append(user)
        requesting_student.save()
        response = user
        error_code = 200

    return response, error_code


@route(bp, "/decline/tutor/<user_id>", methods=['POST'])
@jwt_required()
def post_tutor_decline(user_id):
    requesting_student = users.get_or_404(user_id)

    user = current_user.user
    error_code = 400
    if requesting_student not in user.awaiting_tutor_requests:
        response = {"error_code": 9, "error_message": "There is no request to respond for this user"}
    else:
        user.awaiting_tutor_requests.remove(requesting_student)
        user.save()
        response = user
        error_code = 200

    return response, error_code


@route(bp, "/accept/student/<user_id>", methods=['POST'])
@jwt_required()
def post_tutored_student_accept(user_id):
    requesting_tutor = users.get_or_404(user_id)

    user = current_user.user
    error_code = 400
    if requesting_tutor not in user.awaiting_student_requests:
        response = {"error_code": 9, "error_message": "There is no request to respond for this user"}
    else:
        user.awaiting_student_requests.remove(requesting_tutor)
        user.tutors.append(requesting_tutor)
        user.save()
        requesting_tutor.tutored_students.append(user)
        requesting_tutor.save()
        response = user
        error_code = 200

    return response, error_code


@route(bp, "/decline/student/<user_id>", methods=['POST'])
@jwt_required()
def post_tutored_student_decline(user_id):
    requesting_tutor = users.get_or_404(user_id)

    user = current_user.user
    error_code = 400
    if requesting_tutor not in user.awaiting_student_requests:
        response = {"error_code": 9, "error_message": "There is no request to respond for this user"}
    else:
        user.awaiting_student_requests.remove(requesting_tutor)
        user.save()
        response = user
        error_code = 200

    return response, error_code


@route(bp, "/cancel/tutor/<user_id>", methods=['POST'])
@jwt_required()
def post_cancel_tutor_request(user_id):
    other_user = users.get_or_404(user_id)

    user = current_user.user
    error_code = 400
    if user not in other_user.awaiting_tutor_requests:
        response = {"error_code": 10, "error_message": "There is no request to cancel for this user"}
    else:
        other_user.awaiting_tutor_requests.remove(user)
        other_user.save()
        response = user
        error_code = 200

    return response, error_code


@route(bp, "/cancel/student/<user_id>", methods=['POST'])
@jwt_required()
def post_cancel_student_request(user_id):
    other_user = users.get_or_404(user_id)

    user = current_user.user
    error_code = 400
    if user not in other_user.awaiting_student_requests:
        response = {"error_code": 10, "error_message": "There is no request to cancel for this user"}
    else:
        other_user.awaiting_student_requests.remove(user)
        other_user.save()
        response = user
        error_code = 200

    return response, error_code


@route(bp, "/remove/tutor/<user_id>", methods=['POST'])
@jwt_required()
def post_remove_tutor(user_id):
    other_user = users.get_or_404(user_id)

    user = current_user.user
    other_user.tutored_students.remove(user)
    other_user.save()
    user.tutors.remove(other_user)
    user.save()
    response = user

    return response


@route(bp, "/remove/student/<user_id>", methods=['POST'])
@jwt_required()
def post_remove_student(user_id):
    other_user = users.get_or_404(user_id)

    user = current_user.user
    other_user.tutors.remove(user)
    other_user.save()
    user.tutored_students.remove(other_user)
    user.save()
    response = user

    return response
