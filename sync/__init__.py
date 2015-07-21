def launch_process(config, *args):
    from process import SyncProcess
    from MookAPI.core import db
    from MookAPI.factory import create_app
    from MookAPI.services import local_servers, users

    db.init_app(create_app(__name__, settings_override=config))

    try:
        local_server=local_servers.get(
            key=config.CENTRAL_SERVER_KEY,
            secret=config.CENTRAL_SERVER_SECRET
        )
    except:
        local_server = None

    synchronizer = SyncProcess(
        host=config.CENTRAL_SERVER_HOST,
        key=config.CENTRAL_SERVER_KEY,
        secret=config.CENTRAL_SERVER_SECRET,
        database=db,
        local_server=local_server
    )

    interval = getattr(config, 'SYNC_INTERVAL', None)

    if 'post' in args:
        synchronizer.post_all_documents()

    else:
        if 'reset' in args:
            synchronizer.reset()

        if '-D' in args:
            import daemon
            with daemon.DaemonContext():
                synchronizer.run(interval=interval)
        else:
            synchronizer.run(interval=interval)
