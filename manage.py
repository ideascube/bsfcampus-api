import os, sys, codecs
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask.ext.script import Manager, Server

from MookAPI import app, app_config

sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

def get_port():
	if hasattr(app_config, 'port'):
		return app_config.port
	elif app_config.server_type == 'local':
		return 5001
	else:
		return 5000

manager = Manager(app)

manager.add_command("runserver", Server(
	use_debugger = True,
	use_reloader = True,
	host = '0.0.0.0',
	threaded=True,
	port = get_port()
	)
)

if __name__ == "__main__":
	manager.run()
