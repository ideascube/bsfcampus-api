import flask
import documents
import json
import datetime
from . import bp
from bson import json_util
from flask.ext.security import login_required, roles_required, current_user


@bp.route("/sync")
@login_required
@roles_required('local_server')
def get_local_server_sync_list():
	"""
	Get a list of items to update or delete on the local server.
	"""

	local_server = documents.LocalServer.objects.get_or_404(user=current_user.id)
	
	items = {
		'update': [],
		'delete': [],
	}

	for (index, item) in enumerate(local_server.syncable_items):
		items['update'].extend(item.sync_list()['update'])
		items['delete'].extend(item.sync_list()['delete'])
		local_server.syncable_items[index].last_sync = datetime.datetime.now

	local_server.save()

	return flask.Response(
		response=json_util.dumps({'items': items}),
		mimetype="application/json"
	)


@bp.route("/reset")
@login_required
@roles_required('local_server')
def reset_local_server():
	"""
	Mark all syncable items as never synced.
	"""

	local_server = documents.LocalServer.objects.get_or_404(user=current_user.id)
	
	for (index, item) in enumerate(local_server.syncable_items):
		local_server.syncable_items[index].last_sync = None

	local_server.save()

	return flask.jsonify(local_server=local_server)


@bp.route("/register")
@login_required
@roles_required('local_server')
def register_local_server():
	"""
	Registers the current user as a local server.
	"""

	local_server = documents.LocalServer(user=current_user.id)

	local_server.save()

	return flask.jsonify(local_server=local_server)
