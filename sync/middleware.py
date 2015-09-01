from requests import get, post

class CentralServerConnector(object):

    def __init__(self, host, key, secret, **kwargs):
        self.host = host
        self.key = key
        self.secret = secret
        self.verify_ssl = kwargs.get('verify_ssl', True)

    def get(self, path, **kwargs):
        url = self.host + path
        return get(url, auth=(self.key, self.secret), verify=self.verify_ssl)

    def post(self, path, data=None, json=None):
        url = self.host + path
        return post(url, data=data, json=json, auth=(self.key, self.secret), verify=self.verify_ssl)
