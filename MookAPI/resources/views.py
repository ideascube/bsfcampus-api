import flask
import documents as docs
from . import bp

@bp.route("/")
def get_resources():
	"""GET list of all resources"""

	resources = docs.Resource.objects.all()
	return flask.jsonify(resources=resources)


@bp.route("/<resource_id>")
def get_resource(resource_id):
	"""GET one resource"""

	resource = docs.Resource.objects.get_or_404(id=resource_id)
	return flask.jsonify(resource=resource)
