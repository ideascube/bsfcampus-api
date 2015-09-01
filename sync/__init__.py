import sys

def launch_process(config, *args):
    from middleware import CentralServerConnector
    from process import SyncProcess
    from MookAPI.core import db
    from MookAPI.factory import create_app
    from MookAPI.services import local_servers

    db.init_app(create_app(__name__, settings_override=config))

    connector = CentralServerConnector(
        host=config.CENTRAL_SERVER_HOST,
        key=config.CENTRAL_SERVER_KEY,
        secret=config.CENTRAL_SERVER_SECRET
    )

    if 'reset' in args:
        r = connector.post("/local_servers/reset")
        if r.status_code == 200:
            from settings_local import Config
            db_name = Config.MONGODB_DB # FIXME Get the MongoDB database name from current_app (requires between in app context)
            from mongoengine import connect
            db = connect(db_name)
            db.drop_database(db_name)
            print "Reset successful"
        else:
            sys.exit("Reset failed, status code %d" % r.status_code)

    try:
        local_server = local_servers.get(
            key=config.CENTRAL_SERVER_KEY,
            secret=config.CENTRAL_SERVER_SECRET
        )
    except Exception as e:
        print "This local server is not in the database: trying to fetch from central server"
        r = connector.get("/local_servers/current")
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
                sys.exit(ee.message)


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
