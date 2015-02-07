import flask
import documents as docs
from ..resources import documents as resources_docs
import json
from . import bp

@bp.route("/")
def get_tracks():
	"""GET list of all tracks"""

	print ("GETTING list of all tracks")
	
	tracks = docs.Track.objects.all()
	return flask.jsonify(tracks=tracks)


@bp.route("/<track_id>")
def get_track(track_id):
	"""GET one track"""

	print ("GETTING track with id {track_id}".format(track_id=track_id))
	track = docs.Track.objects.get_or_404(id=track_id)
	return flask.jsonify(track=track)
