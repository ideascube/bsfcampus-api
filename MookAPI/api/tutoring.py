from flask import Blueprint, jsonify
from flask_jwt import current_user

from MookAPI.services import users, tutoring_relations
from MookAPI.auth import jwt_required

from . import route

bp = Blueprint('tutoring', __name__, url_prefix="/tutoring")


@route(bp, "/<relation_id>")
def get_relation(relation_id):
    return tutoring_relations.get(id=relation_id)


@route(bp, "/request/tutor/<user_id>", methods=['POST'], jsonify_wrap=False)
@jwt_required()
def request_tutor(user_id):
    student = current_user.user
    tutor = users.get_or_404(user_id)

    try:
        existing_relation = tutoring_relations.get(tutor=tutor, student=student)

    except:
        new_relation = tutoring_relations.create(
            tutor=tutor,
            student=student,
            initiated_by='student',
            accepted=False
        )

        return jsonify(data=current_user.user)

    else:
        if existing_relation.accepted:
            error_code = 1
            error_message = "This user is already your tutor."
        else:
            if existing_relation.initiated_by == 'student':
                error_code = 2
                error_message = "You already requested this user as a tutor."
            else:
                error_code = 3
                error_message = "This user already requested you as a student."

        return jsonify(
            error_code=error_code,
            error_message=error_message
        ), 400


@route(bp, "/request/student/<user_id>", methods=['POST'], jsonify_wrap=False)
@jwt_required()
def request_student(user_id):
    student = users.get_or_404(user_id)
    tutor = current_user.user

    try:
        existing_relation = tutoring_relations.get(tutor=tutor, student=student)

    except:
        new_relation = tutoring_relations.create(
            tutor=tutor,
            student=student,
            initiated_by='tutor',
            accepted=False
        )

        return jsonify(data=current_user.user)

    else:
        if existing_relation.accepted:
            error_code = 1
            error_message = "This user is already your student."
        else:
            if existing_relation.initiated_by == 'tutor':
                error_code = 2
                error_message = "You already requested this user as a student."
            else:
                error_code = 3
                error_message = "This user already requested you as a tutor."

        return jsonify(
            error_code=error_code,
            error_message=error_message
        ), 400


@route(bp, "/accept/tutor/<user_id>", methods=['POST'], jsonify_wrap=False)
@jwt_required()
def accept_tutor(user_id):
    student = users.get_or_404(user_id)
    tutor = current_user.user

    relation = tutoring_relations.get_or_404(
        tutor=tutor,
        student=student,
        initiated_by='student',
        accepted=False
    )

    relation.accepted = True
    relation.save()

    return jsonify(data=current_user.user)


@route(bp, "/accept/student/<user_id>", methods=['POST'], jsonify_wrap=False)
@jwt_required()
def accept_student(user_id):
    student = current_user.user
    tutor = users.get_or_404(user_id)

    relation = tutoring_relations.get_or_404(
        tutor=tutor,
        student=student,
        initiated_by='tutor',
        accepted=False
    )

    relation.accepted = True
    relation.save()

    return jsonify(data=current_user.user)


@route(bp, "/acknowledge/tutor/<user_id>", methods=['POST'], jsonify_wrap=False)
@jwt_required()
def acknowledge_tutor_relation(user_id):
    student = current_user.user
    tutor = users.get_or_404(user_id)

    relation = tutoring_relations.get_or_404(
        tutor=tutor,
        student=student,
        initiated_by='student',
        accepted=True,
        acknowledged=False
    )

    relation.acknowledged = True
    relation.save()
    return jsonify(data=current_user.user)


@route(bp, "/acknowledge/student/<user_id>", methods=['POST'], jsonify_wrap=False)
@jwt_required()
def acknowledge_student_relation(user_id):
    student = users.get_or_404(user_id)
    tutor = current_user.user

    relation = tutoring_relations.get_or_404(
        tutor=tutor,
        student=student,
        initiated_by='tutor',
        accepted=True,
        acknowledged=False
    )

    relation.acknowledged = True
    relation.save()
    return jsonify(data=current_user.user)


@route(bp, "/decline/tutor/<user_id>", methods=['POST'], jsonify_wrap=False)
@jwt_required()
def decline_tutor(user_id):
    student = users.get_or_404(user_id)
    tutor = current_user.user

    relation = tutoring_relations.get_or_404(
        tutor=tutor,
        student=student,
        initiated_by='student',
        accepted=False
    )

    relation.delete()

    return jsonify(data=current_user.user)


@route(bp, "/decline/student/<user_id>", methods=['POST'], jsonify_wrap=False)
@jwt_required()
def decline_student(user_id):
    student = current_user.user
    tutor = users.get_or_404(user_id)

    relation = tutoring_relations.get_or_404(
        tutor=tutor,
        student=student,
        initiated_by='tutor',
        accepted=False
    )

    relation.delete()

    return jsonify(data=current_user.user)


@route(bp, "/cancel/tutor/<user_id>", methods=['POST'], jsonify_wrap=False)
@jwt_required()
def cancel_tutor_request(user_id):
    student = current_user.user
    tutor = users.get_or_404(user_id)

    relation = tutoring_relations.get_or_404(
        tutor=tutor,
        student=student,
        initiated_by='student',
        accepted=False
    )
    relation.delete()

    return jsonify(data=current_user.user)


@route(bp, "/cancel/student/<user_id>", methods=['POST'], jsonify_wrap=False)
@jwt_required()
def cancel_student_request(user_id):
    student = users.get_or_404(user_id)
    tutor = current_user.user

    relation = tutoring_relations.get_or_404(
        tutor=tutor,
        student=student,
        initiated_by='tutor',
        accepted=False
    )
    relation.delete()

    return jsonify(data=current_user.user)


@route(bp, "/remove/tutor/<user_id>", methods=['POST'], jsonify_wrap=False)
@jwt_required()
def remove_tutor(user_id):
    student = current_user.user
    tutor = users.get_or_404(user_id)

    relation = tutoring_relations.get_or_404(
        tutor=tutor,
        student=student,
        accepted=True
    )
    relation.delete()

    return jsonify(data=current_user.user)


@route(bp, "/remove/student/<user_id>", methods=['POST'], jsonify_wrap=False)
@jwt_required()
def remove_student(user_id):
    student = users.get_or_404(user_id)
    tutor = current_user.user

    relation = tutoring_relations.get_or_404(
        tutor=tutor,
        student=student,
        accepted=True
    )
    relation.delete()

    return jsonify(data=current_user.user)
