def launch_process(config, *args):
    from process import SyncProcess
    from MookAPI.core import db
    from MookAPI.factory import create_app

    db.init_app(create_app(__name__, settings_override=config))

    synchronizer = SyncProcess(
        host=config.CENTRAL_SERVER_HOST,
        key=config.CENTRAL_SERVER_KEY,
        secret=config.CENTRAL_SERVER_SECRET,
        database=db,
        local_server_key=config.CENTRAL_SERVER_KEY,
        local_server_secret=config.CENTRAL_SERVER_SECRET
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
