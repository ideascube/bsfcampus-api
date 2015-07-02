import datetime

from flask import Blueprint, jsonify
from flask_jwt import current_user
from MookAPI.auth import jwt_required

from MookAPI.services import local_servers

from . import route

bp = Blueprint("local_servers", __name__, url_prefix="/local_servers")

@route(bp, "/reset")
@jwt_required()
def reset_local_server():
    user = current_user._get_current_object()
    # FIXME: Check if user has role "local_server"

    local_server = local_servers.first(user=user)

    for (index, item) in enumerate(local_server.syncable_items):
        local_server.syncable_items[index].last_sync = None

    local_server.save()

    return jsonify(data=local_server)

@route(bp, "/sync")
@jwt_required()
def get_local_server_sync_list():
    user = current_user._get_current_object()
    #FIXME: Check if user has role "local_server"

    local_server = local_servers.first(user=user)

    items = dict(update=[], delete=[])

    for (index, item) in enumerate(local_server.syncable_items):
        items['update'].extend(item.sync_list()['update'])
        items['delete'].extend(item.sync_list()['delete'])
        local_server.syncable_items[index].last_sync = datetime.datetime.now

    local_server.save()

    return jsonify(items)

@route(bp, "/register")
@jwt_required()
def register_local_server():

    user = current_user._get_current_object()
    #FIXME: Check if user has role "local_server"

    local_server = local_servers.create(user=user)

    return jsonify(data=local_server)
