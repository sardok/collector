class QueryApiMixin(object):
    """ The mixin which should be used if the class needs to support
    querying collection.

    Model class implements this class as it queries the given collection.

    Query class implements this as it supports the chain of querying.
    """

    def _get_model(self):
        return getattr(self, 'model', None)

    def _create_query(self, query_cls, *args, **kwargs):
        model = self._get_model()
        if isinstance(self, Query):
            kwargs.update(prev=self)
        return query_cls(model, *args, **kwargs)

    def select(self, *args, **kwargs):
        return self._create_query(SelectQuery, *args, **kwargs)

    def when(self, *args, **kwargs):
        return self._create_query(WhenQuery, *args, **kwargs)

    def prefix(self, *args, **kwargs):
        return self._create_query(PrefixQuery, *args, **kwargs)



class Query(QueryApiMixin):
    """ Base class for all querying functions such as select, when etc.

    The subclass should override priority number and implement compile function
    which should return array of (key, val) pairs (tuples).

    Parameters:
    model: Model instance.
    prev: Previous query in the chain (optional).

    """
    # Priority value 0 - 9. Lower means prior process.
    priority = 9

    def __init__(self, model, *args, **kwargs):
        self.model = model
        self.prev = kwargs.pop('prev', None)

    def compile(self):
        raise NotImplementedError

    def get_chain(self):
        res = [self]
        prev = self.prev
        while prev:
            res.append(prev)
            prev = prev.prev
        return res

    def execute(self):
        return self.model.execute(self)


class SelectQuery(Query):
    """ Query class which is returned by select() function. """
    def __init__(self, model, *args, **kwargs):
        super(SelectQuery, self).__init__(model, *args, **kwargs)
        self.keys = args
        self.priority = 1

    def compile(self):
        return [('key', key) for key in self.keys]


class WhenQuery(Query):
    """ Query class which is returned by when() function. """
    def __init__(self, model, *args, **kwargs):
        super(WhenQuery, self).__init__(model, *args, **kwargs)
        self.startts = kwargs.get('startts')
        self.endts = kwargs.get('endts')
        self.priority = 2

    def compile(self):
        res = []
        if self.startts:
            res.append(('startts', self.startts))
        if self.endts:
            res.append(('endts', self.endts))
        return res


class PrefixQuery(Query):
    """ Query class which is returned by prefix() functions. """
    def __init__(self, model, *args, **kwargs):
        super(PrefixQuery, self).__init__(model, *args, **kwargs)
        self.prefixes = args
        self.kwargs = kwargs
        self.priority = 0

    def compile(self):
        res = []
        for prefix in self.prefixes:
            res.append(('prefix', prefix))
        if 'prefixcount' in self.kwargs:
            prefixcount = self.kwargs['prefixcount']
            # Make sure it is integer.
            _ = int(prefixcount)
            res.append(('prefixcount', prefixcount))
        return res
