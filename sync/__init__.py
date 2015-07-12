import sys

def launch_process(*args):
    from settings_local import Config
    from process import SyncProcess
    from MookAPI.core import db
    from MookAPI.factory import create_app

    db.init_app(create_app(__name__, settings_override=Config))

    synchronizer = SyncProcess(
        host=Config.CENTRAL_SERVER_HOST,
        key=Config.CENTRAL_SERVER_KEY,
        secret=Config.CENTRAL_SERVER_SECRET
    )

    interval = getattr(Config, 'SYNC_INTERVAL', None)

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


if __name__ == "__main__":
    launch_process(*sys.argv)
