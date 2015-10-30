from requests import get, post, ConnectionError
import time

class CentralServerConnector(object):

    PATHS = dict(
        reset="/local_servers/reset",
        current_local_server="/local_servers/current",
        fetch_list="/local_servers/sync",
        fetch_whole_track="/local_servers/sync/track/%s",
        fetch_whole_user="/local_servers/sync/user/%s",
        send_documents="/local_servers/add_documents"
    )

    def __init__(self, host, key, secret, local_files_path, **kwargs):
        self.host = host
        self.key = key
        self.secret = secret
        self.local_files_path = local_files_path
        self.verify_ssl = kwargs.get('verify_ssl', True)
        self.connection_error_sleep = kwargs.get('connection_error_sleep', 600)

    def get(self, path):
        url = self.host + path
        try:
            return get(url, auth=(self.key, self.secret), verify=self.verify_ssl)
        except ConnectionError:
            print "Could not connect to the internet: trying again in %d seconds" % self.connection_error_sleep
            time.sleep(self.connection_error_sleep)
            return self.get(path)

    def post(self, path, data=None, json=None):
        url = self.host + path
        try:
            return post(url, data=data, json=json, auth=(self.key, self.secret), verify=self.verify_ssl)
        except ConnectionError:
            print "Could not connect to the internet: trying again in %d seconds" % self.connection_error_sleep
            time.sleep(self.connection_error_sleep)
            return self.post(path, data=data, json=json)


    def fetch_list(self, **kwargs):
        return self.get(self.PATHS["fetch_list"], **kwargs)

    def reset(self, **kwargs):
        return self.post(self.PATHS["reset"], **kwargs)

    def get_current_local_server(self, **kwargs):
        return self.get(self.PATHS["current_local_server"], **kwargs)

    def fetch_list_whole_track(self, track_central_id, **kwargs):
        return self.get(self.PATHS["fetch_whole_track"] % str(track_central_id), **kwargs)

    def fetch_list_whole_user(self, user_central_id, **kwargs):
        return self.get(self.PATHS["fetch_whole_user"] % str(user_central_id), **kwargs)

    def send_documents(self, **kwargs):
        return self.post(self.PATHS["send_documents"], **kwargs)
