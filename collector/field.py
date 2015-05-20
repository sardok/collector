class FieldDescriptor(object):
    def __init__(self, name):
        self.name = name

    def __get__(self, instance, owner):
        return instance.__dict__.get(self.name)

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value


class Field(object):

    def add_to_class(self, obj, name):
        setattr(obj, name, FieldDescriptor(name))
