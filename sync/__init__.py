def launch_process(config, *args):
    from process import SyncProcess
    from MookAPI.core import db
    from MookAPI.factory import create_app

    db.init_app(create_app(__name__, settings_override=config))

    synchronizer = SyncProcess(
        host=config.CENTRAL_SERVER_HOST,
        key=config.CENTRAL_SERVER_KEY,
        secret=config.CENTRAL_SERVER_SECRET
    )

    interval = getattr(config, 'SYNC_INTERVAL', None)

    if 'reset' in args:
        synchronizer.reset()
    elif 'fetch_list' in args:
        synchronizer.fetch_sync_list()
    elif 'next_action' in args:
        synchronizer.next_action()
    elif '-D' in args:
        import daemon
        with daemon.DaemonContext():
            synchronizer.run(interval=interval)
    else:
        synchronizer.run(interval=interval)
