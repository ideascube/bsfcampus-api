from MookAPI import app_config
import threading
import urllib2
from requests import put, get

# delay for test repetition in seconds
delay_after_connection_success = 60 * 60  # 1h
delay_after_connection_fail = 60  # 1m

central_api_host = app_config.central_server_api_host

def test_connection(do_reset):
    print ('test_connection; reset = ' + str(do_reset))
    success = False
    if internet_on():
        if do_reset:
            do_reset = False
            print ('reset')
            response = get('http://localhost:' + str(app_config.port) + '/synchronizer/reset').json()
            print(response)
        print ('fetch_list')
        response = get('http://localhost:' + str(app_config.port) + '/synchronizer/fetch_list').json()
        print (response)
        success = (response.get("error") == 0)
        inc = 0
        while response.get("error") == 0:
            print ('' + str(inc) + '/ depile_item')
            response = get('http://localhost:' + str(app_config.port) + '/synchronizer/depile_item').json()
            print (response)
            inc += 1

    # repeat test after delay
    delay = delay_after_connection_fail
    if success:
        delay = delay_after_connection_success
    print ("delay = " + str(delay))
    threading.Timer(delay, test_connection, do_reset).start()


def internet_on():
    try:
        response = urllib2.urlopen(central_api_host, timeout=5)
        return True
    except urllib2.URLError as err:
        pass
    return False

