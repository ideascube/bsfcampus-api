import flask
import documents as docs
from ..utils import formatObjectToJSONCompliant
from . import bp

@bp.route("/")
def get_resources():
	"""GET list of all resources"""

	resources = docs.Resource.objects.all()
	ret = []
	for resource in resources:
		formattedResource = formatObjectToJSONCompliant(resource, True)
		ret.append(formattedResource)
	return flask.jsonify(resources=ret)


@bp.route("/<resource_id>")
def get_resource(resource_id):
	"""GET one resource"""

	print (resource_id)
	resource = docs.Resource.objects.get_or_404(id=resource_id)
	print("before toJSONObject")
	return flask.jsonify(resource=resource.toJSONObject())
