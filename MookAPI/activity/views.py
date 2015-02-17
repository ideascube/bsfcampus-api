import flask
import documents
import documents.exercise_attempt
from MookAPI.hierarchy import documents as hierarchy_documents
from MookAPI.resources import documents as resources_documents
from MookAPI.resources.documents.exercise_question import *
import json
from . import bp
from bson import json_util
from flask_cors import cross_origin


@bp.route("/ex_attempts", methods=['POST'])
@cross_origin() # allow all origins all methods.
def new_exercise_attempt():
	content = flask.request.get_json(force=True)['attempt']
	print(content)
	id = content['exercise']
	print ("CREATING exercise attempt for exercise {exercise_id}".format(exercise_id=id))
	exercise = resources_documents.Resource.objects.get_or_404(id=id)

	attempt = documents.exercise_attempt.ExerciseAttempt(exercise=exercise)

	return flask.jsonify(attempt=attempt)

