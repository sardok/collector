import logging
from urllib import urlencode
from os import environ
from collector.connection import HttpConnection
from collector.iterators import JsonLinesIterator


class Collection(object):
    base_uri = 'https://storage.scrapinghub.com/collections/'
    http_conn_cls = HttpConnection
    iterator_cls = JsonLinesIterator

    def __init__(self, projectid, collection, apikey=None, store_type='s'):
        allowed_store_types = ['s', 'cs', 'vs', 'vcs']
        if store_type not in allowed_store_types:
            raise RuntimeError('Invalid store type %s (allowed store types: %s)'
                               % (store_type, ', '.join(allowed_store_types)))
        self.endpoint = self.base_uri + '/'.join(
            [str(projectid), store_type, collection])
        if apikey is None:
            apikey = environ.get('SH_APIKEY')
            if apikey is None:
                raise RuntimeError('Apikey must be provided or set as env var.')
        self.conn = self.http_conn_cls(username=apikey)
        logging.basicConfig()
        self.logger = logging.getLogger('Collection')

    def request(self, query):
        url = self.endpoint + '?' + urlencode(query)
        self.logger.debug('Requesting: %s' % url)
        return self.conn.request(url)

    def post(self, data):
        payload = self.iterator_cls.serialize(data)
        self.logger.debug('Posting: %s (data: %r)' % (self.endpoint, payload))
        self.conn.post(self.endpoint, data=payload)

    def delete(self, key):
        return self.conn.delete(self.endpoint + '/' + key)
