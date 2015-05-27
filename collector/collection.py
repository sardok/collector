import logging
from urllib import urlencode
from os import environ
from collector.connection import HttpConnection
from collector.iterators import JsonLinesIterator


class Collection(object):
    """
    A class which provides connection to real collection database.

    Parameters:

    projectid: Project number.
    collection: Collection name.
    apikey: ScrapingHub api key.
    store_type: Storage type (optional, default is 's').

    """
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
        """ Makes a request to the collection database and returns the response.

        Parameters:
        query: Query parameters in array of (key,value) pairs (tuple).

        """
        url = self.endpoint + '?' + urlencode(query)
        self.logger.debug('Requesting: %s' % url)
        return self.conn.request(url)

    def post(self, data):
        """ Makes a post to the collection database and returns the response.

        Parameters:
        data: Should be in dict but in theory could be anything that
        serializer of the iterator class (which JsonLines) support.

        """
        payload = self.iterator_cls.serialize(data)
        self.logger.debug('Posting: %s (data: %r)' % (self.endpoint, payload))
        return self.conn.post(self.endpoint, data=payload)

    def delete(self, key):
        """ Makes a delete request to the collection database and returns the
        response.

        Parameters:
        key: _key attribute of the particular model.

        """
        self.logger.debug('Deleting: %s.' % key)
        return self.conn.delete(self.endpoint + '/' + key)
