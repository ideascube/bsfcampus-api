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
	return flask.jsonify(resources=resources)

@bp.route("/lesson/<lesson_id>")
def get_lesson_resources(lesson_id):
	"""GET list of all resources in given lesson"""

	print ("GETTING list of all resources in lesson {lesson_id}".format(lesson_id=lesson_id))
	
	resources = documents.Resource.objects.order_by('order', 'title').filter(lesson=lesson_id)
	return flask.jsonify(resources=resources)

@bp.route("/skill/<skill_id>")
def get_skill_resources(skill_id):
	"""GET list of all resources in given skill"""

	print ("GETTING list of all resources in skill {skill_id}".format(skill_id=skill_id))
	
	lessons = hierarchy_documents.Lesson.objects.order_by('order', 'title').filter(skill=skill_id)
	resources = documents.Resource.objects.order_by('lesson', 'order', 'title').filter(lesson__in=lessons)
	return flask.jsonify(resources=resources)

@bp.route("/<resource_id>")
def get_resource(resource_id):
	"""GET one resource"""

	print ("GETTING resource with id {resource_id}".format(resource_id=resource_id))
	
	resource = documents.Resource.get_unique_object_or_404(resource_id)
	resource_dict = resource.to_mongo()
	resource_dict['breadcrumb'] = utils.generateBreadcrumb(resource)
	resource_dict['bg_color'] = resource.lesson.skill.track.bg_color

	if isinstance(resource, documents.audio.AudioResource):
		filename = resource.resource_content.audio_file.filename
		resource_dict['resource_content']['content_file_url'] = flask.url_for('resources.get_resource_content_file', resource_id=resource_id, filename=filename, _external=True)
		resource_dict['resource_content']['content_file_name'] = filename
		if resource.resource_content.image:
			resource_dict['resource_content']['content_image_url'] = flask.url_for('resources.get_resource_content_image', resource_id=resource_id, filename=resource.resource_content.image.filename, _external=True)
	elif isinstance(resource, documents.video.VideoResource):
		filename = resource.resource_content.video_file.filename
		resource_dict['resource_content']['content_file_url'] = flask.url_for('resources.get_resource_content_file', resource_id=resource_id, filename=filename, _external=True)
		resource_dict['resource_content']['content_file_name'] = filename
	elif isinstance(resource, documents.downloadable_file.DownloadableFileResource):
		filename = resource.resource_content.downloadable_file.filename
		resource_dict['resource_content']['content_file_url'] = flask.url_for('resources.get_resource_content_file', resource_id=resource_id, filename=filename, _external=True)
		resource_dict['resource_content']['content_file_name'] = filename

	return flask.Response(
		response=json_util.dumps({'resource': resource_dict}),
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
	
	return flask.jsonify(
		resource=resource,
		lesson=lesson,
		skill=skill,
		track=track,
		siblings=resource.siblings(),
		aunts=resource.aunts(),
		cousins=resource.cousins()
	)

@bp.route("/<resource_id>/content-file/<filename>")
def get_resource_content_file(resource_id, filename):
	"""GET one resource's content file"""

	resource = documents.Resource.get_unique_object_or_404(resource_id)
	resource_content = resource.resource_content
	if isinstance(resource_content, documents.audio.AudioResourceContent):
		fileField = resource_content.audio_file
	elif isinstance(resource_content, documents.video.VideoResourceContent):
		fileField = resource_content.video_file
	elif isinstance(resource_content, documents.downloadable_file.DownloadableFileResourceContent):
		fileField = resource_content.downloadable_file
		# fileField.contentType = "application/octet-stream" // we let the browser choose how it handles the file based on its type

	return flask.send_file(io.BytesIO(fileField.read()),
                     attachment_filename=filename,
                     mimetype=fileField.contentType)

@bp.route("/<resource_id>/content-image/<filename>")
def get_resource_content_image(resource_id, filename):
	"""GET one resource's content image"""

	resource = documents.Resource.get_unique_object_or_404(resource_id)
	resource_content = resource.resource_content
	if isinstance(resource_content, documents.audio.AudioResourceContent):
		imageField = resource_content.image

	return flask.send_file(io.BytesIO(imageField.read()),
                     attachment_filename=imageField.filename,
                     mimetype=imageField.contentType)

@bp.route("/tests/create_exercise")
def test_create_exercise():
	
	question1 = unique_answer_mcq.UniqueAnswerMCQExerciseQuestion()
	q1prop1 = unique_answer_mcq.UniqueAnswerMCQExerciseQuestionProposition()
	q1prop1.text = u"A"
	q1prop2 = unique_answer_mcq.UniqueAnswerMCQExerciseQuestionProposition()
	q1prop2.text = u"B"
	q1prop3 = unique_answer_mcq.UniqueAnswerMCQExerciseQuestionProposition()
	q1prop3.text = u"C"
	q1prop4 = unique_answer_mcq.UniqueAnswerMCQExerciseQuestionProposition()
	q1prop4.text = u"D"
	question1.question_text = u"La voyelle ?"
	question1.propositions = [q1prop1, q1prop2, q1prop3, q1prop4]
	q1prop1.is_correct_answer = True

	
	question2 = multiple_answer_mcq.MultipleAnswerMCQExerciseQuestion()
	q2prop1 = multiple_answer_mcq.MultipleAnswerMCQExerciseQuestionProposition()
	q2prop1.text = u"E"
	q2prop2 = multiple_answer_mcq.MultipleAnswerMCQExerciseQuestionProposition()
	q2prop2.text = u"F"
	q2prop3 = multiple_answer_mcq.MultipleAnswerMCQExerciseQuestionProposition()
	q2prop3.text = u"G"
	q2prop4 = multiple_answer_mcq.MultipleAnswerMCQExerciseQuestionProposition()
	q2prop4.text = u"H"
	question2.question_text = u"Les consonnes ?"
	question2.propositions = [q2prop1, q2prop2, q2prop3, q2prop4]
	q2prop2.is_correct_answer = True
	q2prop3.is_correct_answer = True
	q2prop4.is_correct_answer = True
	
	exercise_content = documents.exercise.ExerciseResourceContent()
	exercise_content.questions = [question1, question2]

	exercise = documents.exercise.ExerciseResource()
	exercise.title = u"Alphabet"
	exercise.description = u"Pour apprendre les lettres"
	exercise.lesson = hierarchy_documents.Lesson.objects.first()
	exercise.resource_content = exercise_content

	exercise.save()

	return flask.jsonify(exercise=exercise)
