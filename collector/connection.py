import requests


class HttpConnection(object):
    """ Connects to the collection database by using Http protocol. """
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

    def _send_request(self, request):
        prepped = self.session.prepare_request(request)
        response = self.session.send(prepped)
        return response

    def _do_request(self, method, url, **kw):
        request = requests.Request(method=method, url=url, **kw)
        response = self._send_request(request)
        if response.status_code != 200:
            raise Exception('Server returned unhandled response code: %s'
                            % response.code)
        return response.text

    def request(self, url, **kw):
        """ Makes GET http request, returns response.

        Raises Exception if response' status code is not 200.
        """
        return self._do_request(method='GET', url=url, **kw)

    def post(self, url, **kw):
        """ Makes POST http request, returns response.

        Raises Exception if response' status code is not 200.
        """
        return self._do_request(method='POST', url=url, **kw)

    def delete(self, url, **kw):
        """ Makes DELETE http request, returns response.

        Raises Exception if response' status code is not 200.
        """
        return self._do_request(method='DELETE', url=url, **kw)
