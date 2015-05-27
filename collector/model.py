import logging
from abc import ABCMeta
from itertools import chain
from collections import MutableMapping
from collector.field import Field
from collector.query import QueryApiMixin
from collector.query_result import QueryResult
from collector.utils import flatten


class ModelMeta(ABCMeta):
    def __new__(cls, name, bases, attrs):
        obj = super(ModelMeta, cls).__new__(cls, name, bases, attrs)
        field_names = []
        for name, attr in obj.__dict__.items():
            if isinstance(attr, Field):
                field_names.append(name)
                attr.add_to_class(obj, name)
        setattr(obj, '_field_names', field_names)
        return obj


class Model(MutableMapping, QueryApiMixin):
    """ Main class which is supposed to be a base class for every model
    definition.

    This class supports Query api as well as dict interface.

    Parameters:
    collection: Collection instance.
    logname: Optional string to be used as log identifier.
    Key/Value pairs as field variables and values.

    Attributes:
    _key: Could be used as an identifier of the particular data
    _ts: Timestamp in milliseconds when the data is added to collections.

    """
    __metaclass__ = ModelMeta
    _field_names = []
    _extra_http_queries = [('meta', '_key'), ('meta', '_ts')]
    __key = None
    __ts = None

    def __init__(self, collection, logname=None, **kwargs):
        self.collection = collection
        # Creating model instance variable because of compatibility
        # with Query interface.
        # TODO: include model attribute in QueryApiMixin?
        self.model = self
        logging.basicConfig()
        self._logname = logname or self.__class__.__name__
        self.logger = logging.getLogger(logname)
        self._update_fields(kwargs)
        self.__dict__['_key'] = self._key
        self.__dict__['_ts'] = self._ts

    @property
    def _key(self):
        """ Identifier of the particular data, can be set only, on creation of
        the model instance.
        """
        return self.__key

    @property
    def _ts(self):
        """ Timestamp value in milliseconds which indicates the time of data
        creation and should be assigned by collection server.

        If needed, this value could be set.
        """
        return self.__ts

    def create(self, *a, **kw):
        """ Creates a new instance in which given key/value pairs are assigned
         to relevant Field declarations. Collections instance and logname will
         be implicitly passed to the new instance.

         Example:
         model2 = model.create(_key='new_model', foo=foo_val2, bar=bar_val2)

         In given example, foo and bar Field() attributes of the model, will be
         assigned to foo_val2 and bar_val2 values respectively.
        """
        return type(self)(self.collection, self._logname, *a, **kw)

    def delete(self):
        """ Removes the data from the collection.

        Raises an exception if operation fails.
        """
        self.collection.delete(self._key)

    @staticmethod
    def _sort_chain(qchain):
        return sorted(qchain, key=lambda query: query.priority)

    @staticmethod
    def _get_chain(query):
        return reversed(query.get_chain())

    def _compile_query_chain(self, query_chain):
        query_chain_compiled = [query.compile() for query in query_chain]
        query_chain_compiled.append(self._extra_http_queries)
        return flatten(query_chain_compiled)

    def execute(self, query=None):
        """ Takes optional query parameter as an input and returns query result.

         If query parameter is not given, then all data available in the
         collection server, should be returned.

         Raises an exception if operation fails, returns QueryResult otherwise.
         """
        qchain = self._get_chain(query) if query else []
        qchain = self._sort_chain(qchain)
        params = self._compile_query_chain(qchain)
        result = self.collection.request(params)
        return QueryResult(model=self, result=result)

    def save(self):
        """ Submits all variables of the data (declared as Field),
        regardless of any change, to the collection server.

         Raises an exception, if operation fails.
        """
        updated_data = {'_key': self._key}
        updated_data.update(self._get_fields())
        self.collection.post(updated_data)

    def _update_fields(self, data):
        for key, val in data.items():
            if self._is_field(key):
                setattr(self, key, val)
            else:
                # Set internal non-Field variables.
                if key == '_key':
                    self.__key = val
                elif key == '_ts':
                    self.__ts = val
                else:
                    self.logger.warn('Missing Field declaration: %s.' % key)

    def _get_fields(self):
        filtered_fields = {}
        fields = {name:  getattr(self, name) for name in self._field_names}
        internal_vars = [('_key', self._key), ('_ts', self._ts)]
        for key, val in chain(fields.items(), internal_vars):
            if val is not None:
                filtered_fields[key] = val
        return filtered_fields

    def _is_field(self, item):
        return item in self._field_names

    def __getitem__(self, item):
        if self._is_field(item):
            return getattr(self, item)
        return self.__dict__[item]

    def __setitem__(self, key, value):
        if self._is_field(key):
            object.__setattr__(self, key, value)
        else:
            self.__dict__[key] = value

    def __delitem__(self, key):
        if self._is_field(key):
            self[key] = None
        else:
            del self.__dict__[key]

    def __iter__(self):
        return iter(self._get_fields())

    def __len__(self):
        return len(self._get_fields())

    def __str__(self):
        return str(self._get_fields())
