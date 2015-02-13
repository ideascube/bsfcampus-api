import flask
import documents
from MookAPI.hierarchy import documents as hierarchy_documents
from . import bp


@bp.route("/")
def get_resources():
	"""GET list of all resources"""

	print ("GETTING list of all resources")
	
	resources = documents.Resource.objects.order_by('lesson', 'order', 'title').all()
	return flask.jsonify(resources=resources)

@bp.route("/<resource_id>")
def get_resource(resource_id):
	"""GET one resource"""

	print ("GETTING resource with id {resource_id}".format(resource_id=resource_id))
	
	resource = documents.Resource.get_unique_object_or_404(resource_id)
	return flask.jsonify(resource=resource)

@bp.route("/<resource_id>/hierarchy")
def get_resource_hierarchy(resource_id):
	"""GET one resource"""

	print ("GETTING resource with id {resource_id}".format(resource_id=resource_id))
	
	resource = documents.Resource.get_unique_object_or_404(resource_id)
	
	lesson = resource.lesson
	skill = lesson.skill
	track = skill.track
	
	return flask.jsonify(
		resource=resource,
		lesson=lesson,
		skill=skill,
		track=track,
		siblings=resource.siblings(),
		aunts=resource.aunts(),
		cousins=resource.cousins()
	)
