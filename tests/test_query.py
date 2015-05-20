from unittest import TestCase
from helpers import BasicTestModel


class QueryChainTest(TestCase):
    def test_one_query_chain(self):
        model = BasicTestModel()
        q1 = model.prefix('bar')
        qchain = q1.get_chain()
        self.assertEqual(len(qchain), 1)

    def test_multiple_query_chain(self):
        model = BasicTestModel()
        q1 = model.when()
        q2 = q1.prefix()
        qchain = q2.get_chain()
        self.assertEqual(len(qchain), 2)
        q3 = q2.select()
        qchain = q3.get_chain()
        self.assertEqual(len(qchain), 3)


class QueryOrderTest(TestCase):
    def _check_order(self, names, expected):
        return [n1 == n2 for n1, n2 in zip(names, expected)]

    def _get_class_names(self, obj_list):
        return [obj.__class__.__name__ for obj in obj_list]

    def _check_query_order(self, query, expected):
        qchain = query.get_chain()
        model = query.model
        sorted_chain = model._sort_chain(qchain)
        cls_names = self._get_class_names(sorted_chain)
        return all(self._check_order(cls_names, expected))

    def test_select_vs_when(self):
        model = BasicTestModel()
        query = model.select().when()
        expected = ['SelectQuery', 'WhenQuery']
        self.assertTrue(self._check_query_order(query, expected))

        query = model.when().select()
        self.assertTrue(self._check_query_order(query, expected))

    def test_when_vs_prefix(self):
        model = BasicTestModel()
        query = model.when().prefix()
        expected = ['PrefixQuery', 'WhenQuery']
        self.assertTrue(self._check_query_order(query, expected))

        query = model.prefix().when()
        self.assertTrue(self._check_query_order(query, expected))


class HttpApiQueryTest(TestCase):
    def _compile_query(self, query):
        model = query.model
        qchain = model._get_chain(query)
        qchain = model._sort_chain(qchain)
        return model._compile_query_chain(qchain)

    def test_select(self):
        model = BasicTestModel()
        q1 = model.select('foo')
        query_data = set(self._compile_query(q1))
        self.assertTrue({('key', 'foo')} < query_data)

        q2 = q1.select('bar')
        query_data = set(self._compile_query(q2))
        self.assertTrue({('key', 'foo'), ('key', 'bar')} < query_data)

        q3 = model.select('key1', 'key2')
        query_data = set(self._compile_query(q3))
        self.assertTrue({('key', 'key1'), ('key', 'key2')} < query_data)

    def test_when(self):
        model = BasicTestModel()
        query = model.when(startts=1234, endts=5678)
        query_data = set(self._compile_query(query))
        self.assertTrue({('startts', 1234), ('endts', 5678)} < query_data)

    def test_prefix(self):
        model = BasicTestModel()
        q1 = model.prefix('foo')
        query_data = set(self._compile_query(q1))
        self.assertTrue({('prefix', 'foo')} < query_data)

        q2 = q1.prefix('bar')
        query_data = set(self._compile_query(q2))
        self.assertTrue({('prefix', 'foo'), ('prefix', 'bar')} < query_data)

        q3 = model.prefix('p1', 'p2')
        query_data = set(self._compile_query(q3))
        self.assertTrue({('prefix', 'p1'), ('prefix', 'p2')} < query_data)

    def test_prefixcount(self):
        model = BasicTestModel()
        q1 = model.prefix('foo', prefixcount=5)
        query_data = set(self._compile_query(q1))
        self.assertTrue({('prefix', 'foo'), ('prefixcount', 5)} < query_data)

        q2 = q1.prefix('bar', prefixcount=6)
        query_data = set(self._compile_query(q2))
        self.assertTrue({('prefix', 'foo'), ('prefixcount', 5),
                         ('prefix', 'bar'), ('prefixcount', 6)} < query_data)

        q3 = model.prefix('foo', 'bar', prefixcount=10)
        query_data = set(self._compile_query(q3))
        self.assertTrue({('prefix', 'foo'), ('prefix', 'bar'),
                         ('prefixcount', 10)} < query_data)

