import requests


class HttpConnection(object):
    def __init__(self, username='', password=''):
        self.username = username
        self.password = password
        self.session = self._create_session()

    def _create_session(self):
        s = requests.Session()
        if self.username:
            s.auth = (self.username, '')
        s.stream = True
        return s

    def _do_request(self, request):
        prepped = self.session.prepare_request(request)
        response = self.session.send(prepped)
        return response

    def request(self, url, **kw):
        request = requests.Request(method='GET', url=url, **kw)
        response = self._do_request(request)
        return response.text

    def post(self, url, **kw):
        request = requests.Request(method='POST', url=url, **kw)
        response = self._do_request(request)
        if response.status_code != 200:
            raise Exception('Server returned unhandled response code: %s'
                            % response.code)
        return response.text
