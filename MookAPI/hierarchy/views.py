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
		# tracks_array[key]['skills'] = map(lambda s: s.id, track.skills())
	return json_util.dumps({'tracks': tracks_array})
	# return flask.jsonify(tracks=tracks)

@bp.route("/tracks/<track_id>")
def get_track(track_id):
	"""GET one track"""
	print ("GETTING track {track_id}".format(track_id=track_id))

	track = documents.Track.get_unique_object_or_404(track_id)
	track_dict = track.to_mongo()
	track_dict.skills = map(lambda s: s.id, track.skills())
	return json_util.dumps({'track': track_dict})

@bp.route("/skills")
def get_skills():
	"""GET list of all skills"""
	print ("GETTING list of all skills")
	
	skills = documents.Skill.objects.all()
	return flask.jsonify(skills=skills)

@bp.route("/skills/<skill_id>")
def get_skill(skill_id):
	"""GET one skill"""
	print ("GETTING skill {skill_id}".format(skill_id=skill_id))

	skill = documents.Skill.get_unique_object_or_404(skill_id)
	return flask.jsonify(skill=skill, lessons=skill.lessons())

@bp.route("/lessons")
def get_lessons():
	"""GET list of all lessons"""
	print ("GETTING list of all lessons")
	
	lessons = documents.Lesson.objects.all()
	return flask.jsonify(lessons=lessons)

@bp.route("/lessons/<lesson_id>")
def get_lesson(lesson_id):
	"""GET one lesson"""
	print ("GETTING lesson {lesson_id}".format(lesson_id=lesson_id))

	lesson = documents.lesson.get_unique_object_or_404(lesson_id)
	return flask.jsonify(lesson=lesson, resources=lesson.resources())
