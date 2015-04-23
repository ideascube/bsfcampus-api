import flask
import documents
import MookAPI.hierarchy.documents as hierarchy_documents
import json
import datetime
from . import bp
from bson import json_util
from flask.ext.security import login_required, roles_required, current_user


@bp.route("/")
@login_required
@roles_required('local_server')
def sync_local_server():
	local_server = documents.LocalServer.objects.get_or_404(user=current_user.id)
	
	items = []

	for (index, item) in enumerate(local_server.syncable_items):
		items.append(item.sync_list())
		local_server.syncable_items[index].last_sync = datetime.datetime.now

	local_server.save()

	return flask.Response(
		response=json_util.dumps({'items': items}),
		mimetype="application/json"
		)


@bp.route("/create_local_server")
@login_required
@roles_required('local_server')
def create_local_server():
	local_server = documents.LocalServer()
	local_server.user = current_user

	# track = hierarchy_documents.Track.objects.first()
	# item = documents.SyncableItem()
	# item.item = track
	# local_server.syncable_items = [item]

	local_server.save()

	return flask.jsonify(local_server=local_server)
