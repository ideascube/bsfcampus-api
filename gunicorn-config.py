## This is a trick to find out the server's LAN IP address
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(('8.8.8.8', 80))
local_ip_address = s.getsockname()[0]

## Adress where the server can be accessed
bind = ['127.0.0.1:5000', local_ip_address + ':5000']

## Restart the server when the code changes
reload = True

## Number of workers (allows concurrent requests)
import multiprocessing
workers = multiprocessing.cpu_count() * 2 + 1
