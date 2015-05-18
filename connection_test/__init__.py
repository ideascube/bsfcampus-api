__author__ = 'FredFourcade'

from MookAPI import app_config
import threading
import urllib2
from requests import put, get

# delay for test repetition in seconds
delay = 60 * 60  # 1h

central_api_host = app_config.central_server_api_host


def test_connection():
    if internet_on():
        response = get('http://localhost:' + app_config.port + '/synchronizer/fetch_list').json()
        print (response)
        while response.error == 0:
            response = get('http://localhost:' + app_config.port + '/synchronizer/depile_item').json()

    # repeat test after delay
    threading.Timer(delay, test_connection).start()


def internet_on():
    try:
        response = urllib2.urlopen(central_api_host, timeout=5)
        return True
    except urllib2.URLError as err:
        pass
    return False

