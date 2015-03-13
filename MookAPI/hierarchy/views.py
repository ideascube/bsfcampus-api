import flask
import documents
import MookAPI.resources.documents
import MookAPI.resources.documents.exercise_question
import json
from . import bp
from bson import json_util
import io


@bp.route("/tracks")
def get_tracks():
	"""GET list of all tracks"""
	print ("GETTING list of all tracks")
	
	tracks = documents.Track.objects.order_by('order', 'title').all()
	tracks_array = []
	for ob in tracks:
		track = ob.to_mongo() 
		track['skills'] = map(lambda s: s.id, ob.skills())
		track['imageUrl'] = flask.url_for('hierarchy.get_track_image', track_id=str(ob.id), _external=True)
		tracks_array.append(track)

	return flask.Response(
		response=json_util.dumps({'tracks': tracks_array}),
		mimetype="application/json"
		)

@bp.route("/tracks/<track_id>")
def get_track(track_id):
	"""GET one track"""
	print ("GETTING track {track_id}".format(track_id=track_id))

	track = documents.Track.get_unique_object_or_404(track_id)
	track_dict = track.to_mongo()
	track_dict['skills'] = map(lambda s: s.id, track.skills())
	track_dict['imageUrl'] = flask.url_for('hierarchy.get_track_image', track_id=track_id, _external=True)

	return flask.Response(
		response=json_util.dumps({'track': track_dict}),
		mimetype="application/json"
		)

@bp.route("/tracks/<track_id>/image")
def get_track_image(track_id):
	"""GET image for a specific track"""
	print ("GETTING track {track_id}".format(track_id=track_id))

	track = documents.Track.get_unique_object_or_404(track_id)
	imageField = track.image
	image = imageField.read()

	return flask.send_file(io.BytesIO(image),
                     attachment_filename=imageField.filename,
                     mimetype=imageField.contentType)


@bp.route("/skills")
def get_skills():
	"""GET list of all skills"""
	print ("GETTING list of all skills")
	
	skills = documents.Skill.objects.order_by('track', 'order', 'title').all()
	skills_array = []
	for ob in skills:
		skill = ob.to_mongo();
		skill['lessons'] = map(lambda l: l.id, ob.lessons())
		skill['imageUrl'] = flask.url_for('hierarchy.get_skill_image', skill_id=str(ob.id), _external=True)
		skills_array.append(skill)

	return flask.Response(
		response=json_util.dumps({'skills': skills_array}),
		mimetype="application/json"
		)

@bp.route("/skills/track/<track_id>")
def get_track_skills(track_id):
	"""GET all skills in one track"""
	print ("GETTING skills in track {track_id}".format(track_id=track_id))

	skills = documents.Skill.objects.order_by('order', 'title').filter(track=track_id)
	skills_array = []
	for ob in skills:
		skill = ob.to_mongo();
		skill['lessons'] = map(lambda l: l.id, ob.lessons())
		skill['imageUrl'] = flask.url_for('hierarchy.get_skill_image', skill_id=str(ob.id), _external=True)
		skills_array.append(skill)

	return flask.Response(
		response=json_util.dumps({'skills': skills_array}),
		mimetype="application/json"
		)

@bp.route("/skills/<skill_id>")
def get_skill(skill_id):
	"""GET one skill"""
	print ("GETTING skill {skill_id}".format(skill_id=skill_id))

	skill = documents.Skill.get_unique_object_or_404(skill_id)
	skill_dict = skill.to_mongo()
	skill_dict['lessons'] = map(lambda l: l.id, skill.lessons())
	skill_dict['imageUrl'] = flask.url_for('hierarchy.get_skill_image', skill_id=skill_id, _external=True)

	return flask.Response(
		response=json_util.dumps({'skill': skill_dict}),
		mimetype="application/json"
		)

@bp.route("/skills/<skill_id>/image")
def get_skill_image(skill_id):
	"""GET image for a specific skill"""
	print ("GETTING skill image for skill {skill_id}".format(skill_id=skill_id))

	skill = documents.Skill.get_unique_object_or_404(skill_id)
	imageField = skill.image
	image = imageField.read()

	return flask.send_file(io.BytesIO(image),
                     attachment_filename=imageField.filename,
                     mimetype=imageField.contentType)


@bp.route("/lessons")
def get_lessons():
	"""GET list of all lessons"""
	print ("GETTING list of all lessons")
	
	lessons = documents.Lesson.objects.order_by('skill', 'order', 'title').all()
	lessons_array = [ob.to_mongo() for ob in lessons]
	for (index, lesson) in enumerate(lessons_array):
		lesson['resources'] = map(lambda r: r.id, lessons[index].resources())
		lessons_array[index] = lesson

	return flask.Response(
		response=json_util.dumps({'lessons': lessons_array}),
		mimetype="application/json"
		)

@bp.route("/lessons/skill/<skill_id>")
def get_skill_lessons(skill_id):
	"""GET all lessons in one skill"""
	print ("GETTING lessons in skill {skill_id}".format(skill_id=skill_id))

	lessons = documents.lesson.objects.order_by('order', 'title').filter(skill=skill_id)
	lessons_array = [ob.to_mongo() for ob in lessons]
	for (index, lesson) in enumerate(lessons_array):
		lesson['resources'] = map(lambda r: r.id, lessons[index].resourcess())
		lessons_array[index] = lesson

	return flask.Response(
		response=json_util.dumps({'lessons': lessons_array}),
		mimetype="application/json"
		)

@bp.route("/lessons/<lesson_id>")
def get_lesson(lesson_id):
	"""GET one lesson"""
	print ("GETTING lesson {lesson_id}".format(lesson_id=lesson_id))

	lesson = documents.lesson.get_unique_object_or_404(lesson_id)
	lesson_dict = lesson.to_mongo()
	lesson_dict['resources'] = map(lambda r: r.id, lesson.resources())

	return flask.Response(
		response=json_util.dumps({'lesson': lesson_dict}),
		mimetype="application/json"
		)

@bp.route("/image/<image_id>")
def get_image(image_id):
	"""GET one image from its id"""
	print("GETTING image {image_id}".format(image_id=image_id))

	imageField = documents.images.files.get_or_404(image_id)
	image = imageField.read();

	return send_file(io.BytesIO(image),
                     attachment_filename=imageField.filename,
                     mimetype=imageField.contentType)