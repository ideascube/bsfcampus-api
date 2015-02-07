import flask
import documents as docs
import json
from . import bp

@bp.route("/")
def get_resources():
	"""GET list of all resources"""

	print ("GETTING list of all resources")
	
	resources = docs.Resource.objects.all()
	return flask.jsonify(resources=resources)


@bp.route("/<resource_id>")
def get_resource(resource_id):
	"""GET one resource"""

	print ("GETTING resource with id {resource_id}".format(resource_id=resource_id))
	resource = docs.Resource.objects.get_or_404(id=resource_id)
	return flask.jsonify(resource=resource)
