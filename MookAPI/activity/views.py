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
def post_exercise_attempt():
	exercise_id = json.loads(flask.request.data)['attempt']['exercise']
	exercise = resources_documents.Resource.objects.get_or_404(id=exercise_id)

	print ("CREATING exercise attempt for exercise {exercise}".format(exercise=exercise.id))
	
	attempt = documents.exercise_attempt.ExerciseAttempt().init_with_exercise(exercise)
	attempt.save()

	return flask.jsonify(attempt=attempt)

