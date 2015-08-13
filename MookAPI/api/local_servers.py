import datetime

from flask import abort, Blueprint, jsonify, request

from MookAPI.services import local_servers

from ._security import local_server_required, authenticated_local_server
from . import route

bp = Blueprint("local_servers", __name__, url_prefix="/local_servers")

@route(bp, "/")
def get_all_local_servers():
    return [local_server.to_json_dbref() for local_server in local_servers.all()]

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
    updates, deletes = local_server.get_sync_list()

    references = dict(
        update=[item.to_json_dbref() for item in updates],
        delete=[item.to_json_dbref() for item in deletes]
    )

    local_server.set_last_sync(now)
    local_server.save()

    return references

@route(bp, "/add_item", methods=['POST'])
@local_server_required
def add_item_from_local_server():
    local_server = authenticated_local_server._get_current_object()

    try:
        from bson.json_util import loads
        data = loads(request.get_json())
    except:
        return jsonify(error="Invalid data", code=1), 400

    from MookAPI.helpers import get_service_for_class
    service = get_service_for_class(data['_cls'])
    if not service:
        return jsonify(error="Unrecognized class name", code=2), 400

    obj = service.__model__.from_json(data, from_distant=False)
    obj.save()

    return obj

@route(bp, "/subscribe", methods=['POST'])
@local_server_required
def subscribe_item_to_sync():

    local_server = authenticated_local_server._get_current_object()

    try:
        data = request.get_json()
    except:
        return jsonify(error="Invalid data", code=1), 400
    service_name = data.get('service', None)
    document_id = data.get('document_id', None)

    local_server.append_syncable_item(service_name=service_name, document_id=document_id)

    try:
        local_server.save()
    except Exception as e:
        return jsonify(error=e.message), 400
    else:
        return local_server, 201
