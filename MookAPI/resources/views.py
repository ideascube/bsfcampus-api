import flask
import documents
from documents.exercise_question import *
from MookAPI.hierarchy import documents as hierarchy_documents
from . import bp
from MookAPI import utils
from bson import json_util
import io


@bp.route("/")
def get_resources():
	"""GET list of all resources"""

	print ("GETTING list of all resources")
	
	resources = documents.Resource.objects.order_by('lesson', 'order', 'title').all()

	resources_array = []
	for ob in resources:
		resource = ob.encode_mongo()
		resources_array.append(resource)

	son = {}
	son[documents.Resource.json_key_collection()] = resources_array

	return flask.Response(
		response=json_util.dumps(son),
		mimetype="application/json"
		)

@bp.route("/lesson/<lesson_id>")
def get_lesson_resources(lesson_id):
	"""GET list of all resources in given lesson"""

	print ("GETTING list of all resources in lesson {lesson_id}".format(lesson_id=lesson_id))
	
	resources = documents.Resource.objects.order_by('order', 'title').filter(lesson=lesson_id)

	resources_array = []
	for ob in resources:
		resource = ob.encode_mongo()
		resources_array.append(resource)

	son = {}
	son[documents.Resource.json_key_collection()] = resources_array

	return flask.Response(
		response=json_util.dumps(son),
		mimetype="application/json"
		)

@bp.route("/skill/<skill_id>")
def get_skill_resources(skill_id):
	"""GET list of all resources in given skill"""

	print ("GETTING list of all resources in skill {skill_id}".format(skill_id=skill_id))
	
	lessons = hierarchy_documents.Lesson.objects.order_by('order', 'title').filter(skill=skill_id)
	resources = documents.Resource.objects.order_by('lesson', 'order', 'title').filter(lesson__in=lessons)
	
	resources_array = []
	for ob in resources:
		resource = ob.encode_mongo()
		resources_array.append(resource)

	son = {}
	son[documents.Resource.json_key_collection()] = resources_array

	return flask.Response(
		response=json_util.dumps(son),
		mimetype="application/json"
		)

@bp.route("/<resource_id>")
def get_resource(resource_id):
	"""GET one resource"""

	print ("GETTING resource with id {resource_id}".format(resource_id=resource_id))
	
	resource = documents.Resource.get_unique_object_or_404(resource_id)
	resource_dict = resource.encode_mongo()
	
	son = {}
	son[documents.Resource.json_key()] = resource_dict

	return flask.Response(
		response=json_util.dumps(son),
		mimetype="application/json"
		)

@bp.route("/<resource_id>/hierarchy")
def get_resource_hierarchy(resource_id):
	"""GET one resource's hierarchy"""

	print ("GETTING resource with id {resource_id}".format(resource_id=resource_id))
	
	resource = documents.Resource.get_unique_object_or_404(resource_id)
	
	lesson = resource.lesson
	skill = lesson.skill
	track = skill.track

	son = {}
	son[documents.Resource.json_key()] = resource.encode_mongo()
	son['lesson'] = lesson.encode_mongo()
	son['skill'] = skill.encode_mongo()
	son['track'] = track.encode_mongo()
	son['siblings'] = map(lambda r: r.encode_mongo(), resource.siblings())
	son['aunts'] = map(lambda r: r.encode_mongo(), resource.aunts())
	son['cousins'] = map(lambda r: r.encode_mongo(), resource.cousins())

	return flask.Response(
		response=json_util.dumps(son),
		mimetype="application/json"
		)

@bp.route("/<resource_id>/content-file/<filename>")
def get_resource_content_file(resource_id, filename):
	"""GET one resource's content file"""

	resource = documents.Resource.get_unique_object_or_404(resource_id)
	resource_content = resource.resource_content
	
	if isinstance(resource_content, documents.audio.AudioResourceContent):
		content_file = resource_content.audio_file
	elif isinstance(resource_content, documents.video.VideoResourceContent):
		content_file = resource_content.video_file
	elif isinstance(resource_content, documents.downloadable_file.DownloadableFileResourceContent):
		content_file = resource_content.downloadable_file
		# content_file.contentType = "application/octet-stream" // we let the browser choose how it handles the file based on its type

	return flask.send_file(
		io.BytesIO(content_file.read()),
        attachment_filename=filename,
        mimetype=content_file.contentType
        )

@bp.route("/<resource_id>/content-image/<filename>")
def get_resource_content_image(resource_id, filename):
	"""GET one resource's content image"""

	resource = documents.Resource.get_unique_object_or_404(resource_id)
	resource_content = resource.resource_content

	if isinstance(resource_content, documents.audio.AudioResourceContent):
		content_image = resource_content.image

	return flask.send_file(io.BytesIO(
		content_image.read()),
        attachment_filename=content_image.filename,
        mimetype=content_image.contentType
        )

@bp.route("/<resource_id>/question/<question_id>/image")
def get_question_image(resource_id, question_id):
	"""GET one question's image"""

	resource = documents.Resource.get_unique_object_or_404(resource_id)
	resource_content = resource.resource_content
	for question in resource_content.questions():
		if str(question.id) == question_id:
			question_image = question.question_image
			return flask.send_file(
				io.BytesIO(question_image.read()),
		        attachment_filename=question_image.filename,
		        mimetype=question_image.contentType
		        )

	flask.abort(404)
	