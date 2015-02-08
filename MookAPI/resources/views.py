import flask
import documents
import hierarchy.documents as hierarchy_documents
import json
from . import bp


@bp.route("/")
def get_resources():
	"""GET list of all resources"""

	print ("GETTING list of all resources")
	
	resources = documents.Resource.objects.all()
	return flask.jsonify(resources=resources)

@bp.route("/<resource_id>")
def get_resource(resource_id):
	"""GET one resource"""

	print ("GETTING resource with id {resource_id}".format(resource_id=resource_id))
	
	resource = documents.Resource.objects.get_or_404(id=resource_id)
	
	lesson = resource.lesson
	skill = lesson.skill
	track = skill.track
	
	siblings = documents.Resource.objects(lesson=lesson, id__ne=resource_id)
	aunts = hierarchy_documents.Lesson.objects(skill=skill, id__ne=lesson.id)
	
	return flask.jsonify(
		resource=resource,
		lesson=lesson,
		skill=skill,
		track=track,
		siblings=siblings,
		aunts=aunts
		)
