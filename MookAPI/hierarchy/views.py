import flask
import documents
import json
from . import bp
from bson import json_util

@bp.route("/tracks")
def get_tracks():
	"""GET list of all tracks"""
	print ("GETTING list of all tracks")
	
	tracks = documents.Track.objects.all()
	tracks_array = [ob.to_mongo() for ob in tracks]
	for (index,track) in enumerate(tracks_array):
		track['skills'] = map(lambda s: s.id, tracks[index].skills())
		tracks_array[index] = track

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

	return flask.Response(
		response=json_util.dumps({'track': track_dict}),
		mimetype="application/json"
		)

@bp.route("/skills")
def get_skills():
	"""GET list of all skills"""
	print ("GETTING list of all skills")
	
	skills = documents.Skill.objects.all()
	skills_array = [ob.to_mongo() for ob in skills]
	for (index,skill) in enumerate(skills_array):
		skill['lessons'] = map(lambda s: s.id, skills[index].lessons())
		skills_array[index] = skill

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
	skill_dict['lessons'] = map(lambda s: s.id, skill.lessons())

	return flask.Response(
		response=json_util.dumps({'skill': skill_dict}),
		mimetype="application/json"
		)

@bp.route("/lessons")
def get_lessons():
	"""GET list of all lessons"""
	print ("GETTING list of all lessons")
	
	lessons = documents.Lesson.objects.all()
	lessons_array = [ob.to_mongo() for ob in lessons]
	for (index,lesson) in enumerate(lessons_array):
		lesson['resources'] = map(lambda s: s.id, lessons[index].resources())
		lessons_array[index] = lesson

	return flask.Response(
		response=json_util.dumps({'lessons': lessons_array}),
		mimetype="application/json"
		)

@bp.route("/lessons/<lesson_id>")
def get_lesson(lesson_id):
	"""GET one lesson"""
	print ("GETTING lesson {lesson_id}".format(lesson_id=lesson_id))

	lesson = documents.Lesson.get_unique_object_or_404(lesson_id)
	lesson_dict = lesson.to_mongo()
	lesson_dict['resources'] = map(lambda s: s.id, lesson.resources())

	return flask.Response(
		response=json_util.dumps({'lesson': lesson_dict}),
		mimetype="application/json"
		)
