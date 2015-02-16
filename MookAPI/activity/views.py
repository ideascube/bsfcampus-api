import flask
import documents
import documents.exercise_attempt
from MookAPI.hierarchy import documents as hierarchy_documents
from MookAPI.resources import documents as resources_documents
from MookAPI.resources.documents.exercise_question import *
import json
from . import bp
from bson import json_util


@bp.route("/ex_attempts", methods=['POST'])
def new_exercise_attempt():
	exercise = resources_documents.Resource.objects.get_or_404(id=flask.request.form['exercise_id'])

	attempt = documents.exercise_attempt.ExerciseAttempt(exercise=exercise)

	return flask.jsonify(attempt=attempt)

