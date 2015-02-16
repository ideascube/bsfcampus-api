import flask
import documents
import documents.exercise_attempt
from MookAPI.hierarchy import documents as hierarchy_documents
from MookAPI.resources import documents as resources_documents
from MookAPI.resources.documents.exercise_question import *
import json
from . import bp
from bson import json_util


@bp.route("/tests/create_attempt")
def test_create_exercise_attempt():

	exercise = resources_documents.Resource.objects.get_or_404(id="54e126cee44572df9f752055")

	attempt = documents.exercise_attempt.ExerciseAttempt(exercise=exercise)

	return flask.jsonify(attempt=attempt)
