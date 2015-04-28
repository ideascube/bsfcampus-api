## This is a trick to find out the server's LAN IP address
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(('8.8.8.8', 80))
local_ip_address = s.getsockname()[0]

from MookAPI import app_config
def get_port():
	if hasattr(app_config, 'port'):
		return app_config.port
	elif app_config.server_type == 'local':
		return 5001
	else:
		return 5000

## Adress where the server can be accessed
bind = ['127.0.0.1:' + get_port(), local_ip_address + ':' + get_port()]

## Restart the server when the code changes
reload = True

## Number of workers (allows concurrent requests)
import multiprocessing
workers = multiprocessing.cpu_count() * 2 + 1
