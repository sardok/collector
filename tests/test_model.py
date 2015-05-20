from unittest import TestCase
from collector.field import Field
from collector.exceptions import NoSuchElement
from helpers import BasicTestModel, FixedTestDataMixin


class ModelFieldTest(TestCase):
    def test_field_updates(self):
        class _TestModel(BasicTestModel):
            field1 = Field()
            field2 = Field()

        test_data = {'field1': 'test1', 'field2': 'test2'}
        tm = _TestModel(return_body=test_data)
        self.assertIsNot(any([tm.field1, tm.field2]),
                         'Initial values must be None.')
        first_result = tm.execute().first()
        self.assertEqual(first_result.field1, 'test1')
        self.assertEqual(first_result.field2, 'test2')

    def test_missing_field(self):
        class _TestModel(BasicTestModel):
            field1 = Field()

        test_data = {'field1': 'test1', 'field2': 'test2'}
        tm = _TestModel(return_body=test_data)
        first_result = tm.execute().first()
        self.assertFalse(hasattr(first_result, 'field2'),
                         'Undeclared field must be missing')

    def test_field_value_changes(self):
        class _TestModel(BasicTestModel):
            field1 = Field()

        tm = _TestModel()
        tm.field1 = 'update field1'
        self.assertEqual(tm.field1, 'update field1')


class ModelDataTest(TestCase, FixedTestDataMixin):
    def test_query_all(self):
        tm = self._create_model_for_test_data(self.test_data)
        for data in tm.execute():
            self.assertIn(data, self.test_data)

        all_data = tm.execute().all()
        self.assertTrue(isinstance(all_data, list))
        self.assertEqual(len(all_data), 3)
        for data in all_data:
            self.assertIn(data, self.test_data)

    def test_query_select(self):
        tm = self._create_model_for_test_data(self.test_data)
        entry = tm.select('foo').execute().first()
        self.assertEqual(entry, {'_key': 'foo', 'value': 'foo_value',
                                 'prop': 'foo_prop'})

    def test_query_prefix(self):
        tm = self._create_model_for_test_data(self.test_data)
        result = tm.prefix('ba').execute()
        self.assertEqual(len(result.all()), 2)

    def test_no_such_element(self):
        tm = self._create_model_for_test_data({})
        with self.assertRaises(NoSuchElement):
            tm.execute().first()

        with self.assertRaises(NoSuchElement):
            tm.select('foo').execute().first()

        self.assertListEqual(tm.execute().all(), [])

    def test_update_data(self):
        tm = self._create_model_for_test_data(self.test_data)
        bar = tm.select('bar').execute().first()
        bar.value = 'modified_value'
        bar.save()

        bar2 = tm.select('bar').execute().first()
        self.assertEqual(bar2.value, 'modified_value')

    def test_save(self):
        tm = self._create_model_for_test_data(self.test_data)
        baz = tm.select('baz').execute().first()
        baz.value = 'modified_value'

        baz2 = tm.select('baz').execute().first()
        # raise Exception

        self.assertEqual(baz2.value, 'baz_value')

    def test_immutable_properties(self):
        tm = self._create_model_for_test_data(self.test_data)
        foo = tm.select('foo').execute().first()
        with self.assertRaises(AttributeError):
            foo._key = 'zoo'

        with self.assertRaises(AttributeError):
            foo._ts = 3

    def test_key(self):
        tm = self._create_model_for_test_data(self.test_data)
        self.assertIsNone(tm._key)
        foo = tm.select('foo').execute().first()
        self.assertEqual(foo._key, 'foo')


class ModelDictInterfaceTest(TestCase, FixedTestDataMixin):
    def test_getter(self):
        tm = self._create_model_for_test_data(self.test_data)
        baz = tm.select('baz').execute().first()
        self.assertEqual(baz.prop, 'baz_prop')
        self.assertEqual(baz['prop'], 'baz_prop')

    def test_setter(self):
        tm = self._create_model_for_test_data(self.test_data)
        bar = tm.select('bar').execute().first()
        bar['prop'] = 'prop_modified'
        self.assertEqual(bar.prop, 'prop_modified')
        self.assertEqual(bar['prop'], 'prop_modified')
        bar.save()

        bar2 = tm.select('bar').execute().first()
        self.assertEqual(bar2['prop'], 'prop_modified')

    def test_length(self):
        foo = self._create_model_for_test_data(self.test_data)
        self.assertEqual(len(foo), 3)

    def test_contains(self):
        tm = self._create_model_for_test_data(self.test_data)
        foo = tm.select('foo').execute().first()
        expected = {'prop': 'foo_prop', 'value': 'foo_value'}
        self.assertDictContainsSubset(expected, foo)

        expected['_key'] = 'foo'
        self.assertIn(foo, [expected])
