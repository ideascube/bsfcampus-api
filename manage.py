import os, sys, codecs, multiprocessing

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

from flask.ext.script import Manager, Server
from MookAPI.api import create_app
import settings_central, settings_local

if hasattr(os, 'fork'):
    processes = multiprocessing.cpu_count() * 2 + 1
else:
    processes = 1

def launch_central_server():
    manager = Manager(create_app(settings_override=settings_central.Config))

    manager.add_command(
        'runserver',
        Server(
            host='0.0.0.0',
            port=settings_central.port,
            processes=processes,
            use_reloader=False
        )
    )

    manager.run()


def launch_local_server():
    manager = Manager(create_app(settings_override=settings_local.Config))

    manager.add_command(
        'runserver',
        Server(
            host='0.0.0.0',
            port=settings_local.port,
            processes=processes,
            use_reloader=False
        )
    )

    manager.run()


if __name__ == "__main__":

    if sys.argv[1] == 'sync':
        sys.argv.pop(1)
        from sync import launch_process
        launch_process(settings_local.Config, *sys.argv)

    elif sys.argv[1] == 'runserver':
        if len(sys.argv) > 2:
            if sys.argv.pop(2) == 'local':
                # FIXME: if we do not remove the second argument, the runserver command crashes because it has too many arguments
                launch_local_server()
            else:
                launch_central_server()
        else:
            launch_central_server()
