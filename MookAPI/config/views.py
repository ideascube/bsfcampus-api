import flask
import documents
import json
from . import bp
from bson import json_util

@bp.route("/parameters")
def get_all_parameters():
	"""GET list of all config parameters"""
	print ("GETTING all parameters concatenated")
	
	parameters_list = documents.ConfigParameters.objects.all()
	parameters_dict = dict()
	for ob in parameters_list:
		parameters = ob.to_mongo()
		parameters_dict[parameters['name']] = json_util.loads(ob.parameters)

	return flask.Response(
		response=json_util.dumps(parameters_dict),
		mimetype="application/json"
		)

@bp.route("/parameters/<parameters_group_id>")
def get_parameters_group(parameters_group_id):
	"""GET one parameters group"""
	print ("GETTING parameters group {parameters_group_id}".format(parameters_group_id=parameters_group_id))

	parametersDoc = documents.ConfigParameters.get_unique_object_or_404(parameters_group_id)

	return flask.Response(
		response=json_util.dumps({parametersDoc.name: json_util.loads(parametersDoc.parameters)}),
		mimetype="application/json"
		)