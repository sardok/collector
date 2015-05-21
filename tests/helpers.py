import itertools
from collector.model import Model
from collector.field import Field
from collector.iterators import JsonLinesIterator

class BasicTestCollection(object):
    iterator_cls = JsonLinesIterator

    def __init__(self, return_body=None):
        return_body = return_body or ''
        if isinstance(return_body, basestring):
            self.return_body = return_body
        else:
            self.return_body = self.iterator_cls.serialize(return_body)

    def request(self, *a, **kw):
        return self.return_body


class BasicTestModel(Model):

    def __init__(self, collection=None, return_body=None, *args, **kwargs):
        collection = collection or BasicTestCollection(return_body)
        super(BasicTestModel, self).__init__(collection, *args, **kwargs)


class StubCollection(object):
    iterator_cls = iter

    """ A Basic Stub Collection class """
    def __init__(self, *a, **kw):
        self.data = kw.pop('data', [])

    def _process_key(self, keys, data):
        return [d for d in data for key in keys if d.get('_key') == key]

    def _process_prefix(self, param, data):
        return [d for d in data for p in param
                if d.get('_key', '').startswith(p)]

    def _process_data(self, params):
        res = self.data
        grouped = itertools.groupby(params, lambda x: x[0])
        for key, tuple_list in grouped:
            values = [value for _, value in tuple_list]
            func = getattr(self, '_process_%s' % key, lambda param, data: data)
            res = func(values, res)
        return res

    def request(self, params=None):
        params = params or []
        return self._process_data(params)

    def post(self, params=None):
        params = params or {}
        key = params.get('_key')
        entries = self._process_key([key], self.data)
        if entries:
            entry = entries[0]
            entry.update(params)
        else:
            # Create new entry.
            self.data.append(params)

    def delete(self, key):
        self.data = [d for d in self.data if d.get('_key') != key]


class FixedTestDataMixin(object):
    __test_data = [
        {'_key': 'foo', 'value': 'foo_value', 'prop': 'foo_prop'},
        {'_key': 'bar', 'value': 'bar_value', 'prop': 'bar_prop'},
        {'_key': 'baz', 'value': 'baz_value', 'prop': 'baz_prop'},
    ]

    @property
    def test_data(self):
        return self.__test_data

    def _create_model_for_test_data(self, data):
        class TestModel(Model):
            value = Field()
            prop = Field()

            def _get_fields(self):
                fields = super(TestModel, self)._get_fields()
                if '_ts' in fields:
                    del fields['_ts']
                return fields

        return TestModel(collection=StubCollection(data=data))
