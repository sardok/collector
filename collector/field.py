class FieldDescriptor(object):
    def __init__(self, name):
        self.name = name

    def __get__(self, instance, owner):
        return instance.__dict__.get(self.name)

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value


class Field(object):
    """ Allows to bind a variable on the collection database to the Model
    attribute.

    Example:

    class FooModel(Model):
        value = Field()
        another_value = Field()


    Here, the FooModel's value and another_value attributes will be bound
    to the exactly same parameters on the collection instance.
    """

    def add_to_class(self, obj, name):
        setattr(obj, name, FieldDescriptor(name))
