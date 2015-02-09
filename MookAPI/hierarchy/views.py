import flask
import documents
from . import bp


@bp.route("/")
def get_tracks():
	"""GET list of all tracks"""
	print ("GETTING list of all tracks")
	
	tracks = documents.Track.objects.all()
	return flask.jsonify(tracks=tracks)

@bp.route("/<track_id>")
def get_track(track_id):
	"""GET one track"""
	print ("GETTING track {track_id}".format(track_id=track_id))

	track = documents.Track.get_unique_object_or_404(track_id)
	return flask.jsonify(track=track, skills=track.skills())

@bp.route("/<track_id>/<skill_id>")
def get_skill(track_id,skill_id):
	"""GET one skill"""
	print ("GETTING skill {skill_id}".format(skill_id=skill_id))

	skill = documents.Skill.get_unique_object_or_404(skill_id, track_id)
	return flask.jsonify(skill=skill, lessons=skill.lessons())

@bp.route("/<track_id>/<skill_id>/<lesson_id>")
def get_lesson(track_id,skill_id,lesson_id):
	"""GET one lesson"""
	print ("GETTING lesson {lesson_id}".format(lesson_id=lesson_id))

	lesson = documents.Lesson.get_unique_object_or_404(lesson_id, skill_id, track_id)
	return flask.jsonify(lesson=lesson, resources=lesson.resources())

