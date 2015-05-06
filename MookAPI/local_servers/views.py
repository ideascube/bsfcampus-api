import io
import datetime

import flask
from flask.ext import restful
from flask.ext.security import login_required, roles_required, current_user

from MookAPI import api
import documents


class CentralServerResetLocalServerView(restful.Resource):

    @login_required
    @roles_required('local_server')
    def get(self):
        """
        Mark all syncable items as never synced.
        """

        local_server = documents.LocalServer.objects.get_or_404(user=current_user.id)
        
        for (index, item) in enumerate(local_server.syncable_items):
            local_server.syncable_items[index].last_sync = None

        local_server.save()

        return local_server

api.add_resource(CentralServerResetLocalServerView, '/local_servers/reset', endpoint='central_server_reset_local_server')

class CentralServerSyncListView(restful.Resource):

    @login_required
    @roles_required('local_server')
    def get(self):
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

        return {'items': items}

api.add_resource(CentralServerSyncListView, '/local_servers/sync', endpoint='central_server_sync_list')


class CentralServerRegisterLocalServerView(restful.Resource):

    @login_required
    @roles_required('local_server')
    def get(self):
        """
        Registers the current user as a local server.
        """

        local_server = documents.LocalServer(user=current_user.id)

        local_server.save()

        return local_server

api.add_resource(CentralServerRegisterLocalServerView, '/local_servers/register', endpoint='central_server_register_local_server')
