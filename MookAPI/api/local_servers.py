import datetime

from flask import abort, Blueprint, jsonify, request

from MookAPI.services import local_servers

from ._security import basic_auth_required, basic_auth_user
from . import route

bp = Blueprint("local_servers", __name__, url_prefix="/local_servers")

@route(bp, "/current")
@basic_auth_required
def get_current_local_server():
    user = basic_auth_user._get_current_object()
    # FIXME: Check if user has role "local_server"

    return local_servers.get_or_404(user=user)

@route(bp, "/<local_server_id>")
@basic_auth_required
def get_local_server(local_server_id):
    user = basic_auth_user._get_current_object()
    # FIXME: Check if user has role "local_server"

    local_server = local_servers.get_or_404(id=local_server_id)
    if local_server.user != user:
        abort(401)

    return local_server

@route(bp, "/reset")
@basic_auth_required
def reset_local_server():
    user = basic_auth_user._get_current_object()
    # FIXME: Check if user has role "local_server"

    local_server = local_servers.get_or_404(user=user)

    local_server.reset()

    local_server.save()

    return local_server

@route(bp, "/sync")
@basic_auth_required
def get_local_server_sync_list():
    user = basic_auth_user._get_current_object()
    #FIXME: Check if user has role "local_server"

    local_server = local_servers.get_or_404(user=user)
    now = datetime.datetime.now
    updates, deletes = local_server.get_sync_list()

    references = dict(
        update=[item.to_json_dbref() for item in updates],
        delete=[item.to_json_dbref() for item in deletes]
    )

    local_server.set_last_sync(now)
    local_server.save()

    return references

@route(bp, "/add_item", methods=['POST'], jsonify_wrap=False)
@basic_auth_required
def add_item_from_local_server():
    user = basic_auth_user._get_current_object()
    #FIXME: Check if user has role "local_server"

    local_server = local_servers.get_or_404(user=user)

    try:
        from bson.json_util import loads
        data = loads(request.get_json())
    except:
        return jsonify(error="Invalid data", code=1), 400

    from MookAPI.helpers import _get_service_for_class
    service = _get_service_for_class(data['_cls'])
    if not service:
        return jsonify(error="Unrecognized class name", code=2), 400

    obj = service.__model__.from_json(data)
    obj.save()

    return jsonify(data=obj)

@route(bp, "/register", methods=['POST'])
@basic_auth_required
def register_local_server():

    user = basic_auth_user._get_current_object()
    #FIXME: Check if user has role "local_server"

    local_server = local_servers.create(user=user)

    return local_server

@route(bp, "/subscribe", methods=['POST'], jsonify_wrap=False)
@basic_auth_required
def subscribe_item_to_sync():

    user = basic_auth_user._get_current_object()
    #FIXME: Check if user has role "local_server"

    local_server = local_servers.get_or_404(user=user)

    try:
        data = request.get_json()
    except:
        return jsonify(error="Invalid data", code=1), 400
    service_name = data.get('service', None)
    document_id = data.get('document_id', None)

    local_server.append_syncable_item(service_name, document_id)

    try:
        local_server.save()
    except Exception as e:
        return jsonify(error=e.message), 400
    else:
        return jsonify(data=local_server)
