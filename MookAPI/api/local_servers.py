import datetime
import os

from flask import abort, Blueprint, jsonify, request, current_app, redirect

from MookAPI.services import local_servers

from ._security import local_server_required, authenticated_local_server
from . import route

bp = Blueprint("local_servers", __name__, url_prefix="/local_servers")

@route(bp, "/")
def get_all_local_servers():
    list = [local_server.to_json_dbref() for local_server in local_servers.all()]
    return jsonify(data=list)

@route(bp, "/batch_load", methods=["POST"])
def batch_load_local_servers():
    def allowed_file(filename):
        ALLOWED_EXTENSIONS = ("csv")
        return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

    file = request.files['csv_file']
    if file and allowed_file(file.filename):
        created_local_servers = []
        import csv
        reader = csv.DictReader(file)
        for row in reader:
            if ('synced_tracks' in row) and row['synced_tracks']:
                row['synced_tracks'] = row['synced_tracks'].split("|")
            else:
                del row['synced_tracks']
            try:
                local_server = local_servers.create(**row)
            except Exception as e:
                return jsonify(
                    created_local_servers=created_local_servers,
                    error=e.message
                )
            else:
                created_local_servers.append(local_server)
        return jsonify(
            created_local_servers=created_local_servers
        )
    return jsonify(error="Could not read CSV file")

@route(bp, "/current")
@local_server_required
def get_current_local_server():
    return authenticated_local_server._get_current_object()

@route(bp, "/<local_server_id>")
@local_server_required
def get_local_server(local_server_id):
    local_server = local_servers.get_or_404(id=local_server_id)
    if authenticated_local_server._get_current_object().id != local_server.id:
        abort(401)

    return local_server

@route(bp, "/reset", methods=['POST'])
@local_server_required
def reset_local_server():
    local_server = authenticated_local_server._get_current_object()

    local_server.reset()

    local_server.save()

    return local_server

@route(bp, "/sync")
@local_server_required
def get_local_server_sync_list():
    local_server = authenticated_local_server._get_current_object()
    now = datetime.datetime.now
    sync_list = local_server.get_sync_list()

    references = dict(
        updates=[item.to_json_dbref() for item in sync_list['updates']],
        deletes=sync_list['deletes'] # Those are dictionaries containing the class name and a DBRef
    )

    local_server.last_sync = now
    local_server.save()

    return jsonify(data=references)

@route(bp, "/sync/track/<track_id>")
@local_server_required
def get_track_sync_documents(track_id):
    local_server = authenticated_local_server._get_current_object()
    from MookAPI.services import tracks

    track = tracks.get(id=track_id)

    references = dict(
        updates=[document.to_json_dbref() for document in track.all_synced_documents(local_server)],
    )

    return jsonify(data=references)

@route(bp, "/sync/user/<user_id>")
@local_server_required
def get_user_sync_documents(user_id):
    local_server = authenticated_local_server._get_current_object()
    from MookAPI.services import users

    user = users.get(id=user_id)

    references = dict(
        updates=[document.to_json_dbref() for document in user.all_synced_documents(local_server)],
    )

    return jsonify(data=references)

@route(bp, "/add_documents", methods=['POST'])
@local_server_required
def add_documents_from_local_server():
    local_server = authenticated_local_server._get_current_object()

    try:
        from bson.json_util import loads
        documents = loads(request.get_json())
    except:
        return jsonify(error="Invalid data", code=1), 400

    from MookAPI.helpers import get_service_for_class
    new_documents = []
    for (id, document) in documents:
        service = get_service_for_class(document['_cls'])
        if not service:
            return jsonify(error="Unrecognized class name", code=2), 400

        obj = service.__model__.from_json(document, from_central=False)
        obj.save()
        new_documents.append((id, obj))

    return jsonify(data=new_documents)
