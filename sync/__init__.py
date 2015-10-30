import sys

from documents import SyncTasksService
from middleware import CentralServerConnector
from process import SyncProcess
from MookAPI.factory import create_app
from MookAPI.services import local_servers

sync_tasks_service = SyncTasksService()

def launch_process(config, *args):

    from MookAPI.core import db
    db.init_app(create_app(__name__, settings_override=config))

    connector = CentralServerConnector(
        host=config.CENTRAL_SERVER_HOST,
        key=config.CENTRAL_SERVER_KEY,
        secret=config.CENTRAL_SERVER_SECRET,
        local_files_path=config.UPLOAD_FILES_PATH,
        connection_error_sleep=getattr(config, "CONNECTION_ERROR_SLEEP", 600)
    )

    if 'reset' in args:
        r = connector.reset()
        if r.status_code == 200:
            from settings_local import Config
            db_name = Config.MONGODB_DB # FIXME Get the MongoDB database name from current_app (requires between in app context)
            from mongoengine import connect
            db = connect(db_name)
            db.drop_database(db_name)
            print "Reset successful"
        else:
            sys.exit("Reset failed, status code %d" % r.status_code)

    local_server = None
    try:
        local_server = local_servers.get(
            key=config.CENTRAL_SERVER_KEY,
            secret=config.CENTRAL_SERVER_SECRET
        )
    except Exception as e:
        print "This local server is not in the database: trying to fetch from central server"
        r = connector.get_current_local_server()
        if r.status_code == 200:
            try:
                from bson import json_util
                son = json_util.loads(r.text)
                local_server = local_servers.__model__.from_json(
                    son['data'],
                    from_central=True
                )
                local_server.clean()
                local_server.save(validate=False) # FIXME MongoEngine bug, hopefully be fixed in next version
            except Exception as ee:
                sys.exit("The local server was unable to instantiate its DB representation: %s" % ee.message)

    if not local_server:
        sys.exit("The local server was unable to instantiate its DB representation")

    synchronizer = SyncProcess(
        connector=connector,
        local_server=local_server
    )

    interval = getattr(config, 'SYNC_INTERVAL', None)

    if '-D' in args:
        import daemon
        with daemon.DaemonContext():
            synchronizer.run(interval=interval)
    else:
        synchronizer.run(interval=interval)
