import flask
import documents
import MookAPI.resources.documents
import MookAPI.resources.documents.exercise_question
import json
from . import bp
from MookAPI import utils
from bson import json_util
import io


@bp.route("/tracks")
def get_tracks():
	"""GET list of all tracks"""
	print ("GETTING list of all tracks")
	
	tracks = documents.Track.objects.order_by('order', 'title').all()
	tracks_array = []
	for ob in tracks:
		track = ob.encode_mongo()
		tracks_array.append(track)

	son = {}
	son[documents.Track.json_key_collection()] = tracks_array

	return flask.Response(
		response=json_util.dumps(son),
		mimetype="application/json"
		)

@bp.route("/tracks/<track_id>")
def get_track(track_id):
	"""GET one track"""
	print ("GETTING track {track_id}".format(track_id=track_id))

	track = documents.Track.get_unique_object_or_404(track_id)
	track_dict = track.encode_mongo()

	son = {}
	son[documents.Track.json_key()] = track_dict

	return flask.Response(
		response=json_util.dumps(son),
		mimetype="application/json"
		)

@bp.route("/tracks/<track_id>/icon")
def get_track_icon(track_id):
	"""GET icon image for a specific track"""
	print ("GETTING track icon for track {track_id}".format(track_id=track_id))

	track = documents.Track.get_unique_object_or_404(track_id)
	imageField = track.icon
	image = imageField.read()

	return flask.send_file(io.BytesIO(image),
		attachment_filename=imageField.filename,
		mimetype=imageField.contentType
		)


@bp.route("/skills")
def get_skills():
	"""GET list of all skills"""
	print ("GETTING list of all skills")
	
	skills = documents.Skill.objects.order_by('track', 'order', 'title').all()
	skills_array = []
	for ob in skills:
		skill = ob.encode_mongo()
		skills_array.append(skill)

	son = {}
	son[documents.Skill.json_key_collection()] = skills_array

	return flask.Response(
		response=json_util.dumps(son),
		mimetype="application/json"
		)

@bp.route("/skills/track/<track_id>")
def get_track_skills(track_id):
	"""GET all skills in one track"""
	print ("GETTING skills in track {track_id}".format(track_id=track_id))

	skills = documents.Skill.objects.order_by('order', 'title').filter(track=track_id)
	skills_array = []
	for ob in skills:
		skill = ob.encode_mongo()
		skills_array.append(skill)

	son = {}
	son[documents.Skill.json_key_collection()] = skills_array

	return flask.Response(
		response=json_util.dumps(son),
		mimetype="application/json"
		)

@bp.route("/skills/<skill_id>")
def get_skill(skill_id):
	"""GET one skill"""
	print ("GETTING skill {skill_id}".format(skill_id=skill_id))

	skill = documents.Skill.get_unique_object_or_404(skill_id)
	skill_dict = skill.encode_mongo()

	son = {}
	son[documents.Skill.json_key()] = skill_dict

	return flask.Response(
		response=json_util.dumps({'skill': skill_dict}),
		mimetype="application/json"
		)

@bp.route("/skills/<skill_id>/icon")
def get_skill_icon(skill_id):
	"""GET icon image for a specific skill"""
	print ("GETTING skill icon for skill {skill_id}".format(skill_id=skill_id))

	skill = documents.Skill.get_unique_object_or_404(skill_id)
	imageField = skill.icon
	image = imageField.read()

	return flask.send_file(io.BytesIO(image),
		attachment_filename=imageField.filename,
		mimetype=imageField.contentType
		)


@bp.route("/lessons")
def get_lessons():
	"""GET list of all lessons"""
	print ("GETTING list of all lessons")
	
	lessons = documents.Lesson.objects.order_by('skill', 'order', 'title').all()
	lessons_array = [ob.encode_mongo() for ob in lessons]

	son = {}
	son[documents.Lesson.json_key_collection()] = lessons_array

	return flask.Response(
		response=json_util.dumps(son),
		mimetype="application/json"
		)

@bp.route("/lessons/skill/<skill_id>")
def get_skill_lessons(skill_id):
	"""GET all lessons in one skill"""
	print ("GETTING lessons in skill {skill_id}".format(skill_id=skill_id))

	lessons = documents.Lesson.objects.order_by('order', 'title').filter(skill=skill_id)
	lessons_array = [ob.encode_mongo() for ob in lessons]

	son = {}
	son[documents.Lesson.json_key_collection()] = lessons_array

	return flask.Response(
		response=json_util.dumps(son),
		mimetype="application/json"
		)

@bp.route("/lessons/<lesson_id>")
def get_lesson(lesson_id):
	"""GET one lesson"""
	print ("GETTING lesson {lesson_id}".format(lesson_id=lesson_id))

	lesson = documents.Lesson.get_unique_object_or_404(lesson_id)
	lesson_dict = lesson.encode_mongo()

	son = {}
	son[documents.Lesson.json_key()] = lesson_dict

	return flask.Response(
		response=json_util.dumps(son),
		mimetype="application/json"
		)
