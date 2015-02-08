import flask
import documents
from .. import documents as resources_documents
from .. import bp


@bp.route("/tracks")
def get_tracks():
	"""GET list of all tracks"""

	print ("GETTING list of all tracks")
	
	tracks = documents.Track.objects.all()
	return flask.jsonify(tracks=tracks)

@bp.route("/tracks/<track_id>")
def get_track(track_id):
	"""GET one track"""

	print ("GETTING track with id {track_id}".format(track_id=track_id))
	track = documents.Track.objects.get_or_404(id=track_id)
	return flask.jsonify(track=track, skills=track.skills())

@bp.route("/tracks/<track_id>/skills")
def get_skills(track_id):
	"""GET list of skills in track"""

	print ("GETTING skills in track {track_id}".format(track_id=track_id))
	track = documents.Track.objects.get_or_404(id=track_id)
	return flask.jsonify(skills=track.skills())

@bp.route("/skills/<skill_id>")
def get_skill(skill_id):
	"""GET one skill"""

	print ("GETTING skill with id {skill_id}".format(skill_id=skill_id))
	skill = documents.Skill.objects.get_or_404(id=skill_id)
	return flask.jsonify(skill=skill, lessons=skill.lessons())

@bp.route("/skills/<skill_id>/lessons")
def get_lessons(skill_id):
	"""GET list of lessons in skill"""

	print ("GETTING lessons in skill {skill_id}".format(skill_id=skill_id))
	skill = documents.Skill.objects.get_or_404(id=skill_id)
	return flask.jsonify(lessons=skill.lessons())

@bp.route("/lessons/<lesson_id>")
def get_lesson(lesson_id):
	"""GET one lesson"""

	print ("GETTING lesson with id {lesson_id}".format(lesson_id=lesson_id))
	lesson = documents.Lesson.objects.get_or_404(id=lesson_id)
	return flask.jsonify(lesson=lesson, resources=lesson.resources())
