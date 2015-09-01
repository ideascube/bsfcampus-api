import datetime

from flask import abort, Blueprint, jsonify, request

from MookAPI.services import local_servers

from ._security import local_server_required, authenticated_local_server
from . import route

bp = Blueprint("local_servers", __name__, url_prefix="/local_servers")

@route(bp, "/")
def get_all_local_servers():
    list = [local_server.to_json_dbref() for local_server in local_servers.all()]
    return jsonify(data=list)

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

@route(bp, "/add_item", methods=['POST'])
@local_server_required
def add_item_from_local_server():
    """Deprecated. Use the add_items route instead"""

    local_server = authenticated_local_server._get_current_object()

    try:
        from bson.json_util import loads
        item = loads(request.get_json())
    except:
        return jsonify(error="Invalid data", code=1), 400

    from MookAPI.helpers import get_service_for_class
    service = get_service_for_class(item['_cls'])
    if not service:
        return jsonify(error="Unrecognized class name", code=2), 400

    obj = service.__model__.from_json(item, from_central=False)
    obj.save()

    return obj

@route(bp, "/add_items", methods=['POST'])
@local_server_required
def add_items_from_local_server():
    local_server = authenticated_local_server._get_current_object()

    try:
        from bson.json_util import loads
        data = loads(request.get_json())
    except:
        return jsonify(error="Invalid data", code=1), 400

    from MookAPI.helpers import get_service_for_class
    central_items = dict()
    for local_id, item in data['items']:
        try:
            service = get_service_for_class(item['_cls'])
            if not service:
                pass # TODO Generate an error

            obj = service.__model__.from_json(item, from_central=False)
            obj.save()
        except:
            pass # TODO Generate an error
        else:
            central_items[local_id] = obj

    return jsonify(data=dict(items=central_items)), 201
