from unittest import TestCase
from collector.field import Field, FieldDescriptor
from helpers import BasicTestModel


class ExpectedException(Exception):
    pass


class FieldTest(TestCase):
    def _get_field_with_description(self, desc_cls):

        class TestField(Field):
            def add_to_class(self, obj, name):
                setattr(obj, name, desc_cls(name))

        return TestField

    def test_field_description_set(self):

        class TestFieldDescription(FieldDescriptor):
            def __set__(self, instance, value):
                raise ExpectedException

        field_cls = self._get_field_with_description(TestFieldDescription)

        class FieldTestModel(BasicTestModel):
            myvar = field_cls()

        tm = FieldTestModel()
        with self.assertRaises(ExpectedException):
            tm.myvar = 5

    def test_field_description_get(self):

        class TestFieldDescription(FieldDescriptor):
            def __get__(self, instance, owner):
                raise ExpectedException

        field_cls = self._get_field_with_description(TestFieldDescription)

        class FieldTestModel(BasicTestModel):
            myvar = field_cls()

        tm = FieldTestModel()
        with self.assertRaises(ExpectedException):
            tm.myvar

        tm.myvar = 10
        with self.assertRaises(ExpectedException):
            tm.myvar
