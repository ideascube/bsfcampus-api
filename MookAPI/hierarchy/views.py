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
	track = documents.Track.objects.get_or_404(id=track_id)
	return flask.jsonify(track=track, skills=track.skills())

@bp.route("/<track_id>/<skill_id>")
def get_skill(track_id,skill_id):
	"""GET one skill"""

	print ("GETTING skill {skill_id}".format(skill_id=skill_id))
	skill = documents.Skill.objects.get_or_404(
		id=skill_id,
		track=track_id
		)
	return flask.jsonify(skill=skill, lessons=skill.lessons())

@bp.route("/<track_id>/<skill_id>/<lesson_id>")
def get_lesson(track_id,skill_id,lesson_id):
	"""GET one lesson"""

	print ("GETTING lesson {lesson_id}".format(lesson_id=lesson_id))
	# The following command ensures that the skill belongs to the track.
	# It is not strictly needed
	skill = documents.Skill.objects.get_or_404(
		id=skill_id,
		track=track_id,
		)
	lesson = documents.Lesson.objects.get_or_404(
		id=lesson_id,
		skill=skill,
		)
	return flask.jsonify(lesson=lesson, resources=lesson.resources())

