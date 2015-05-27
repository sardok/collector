# Collector
An ORM library for Scrapinghub Collections API which uses HTTP requests to communicate with data storage. 

For more about Collections API, please visit http://doc.scrapinghub.com/collections.html

## Examples
Say, we have collection with following initial data:

```python
{'_key': u'foo', 'another_value': u'another_bar', 'value': u'bar'}
{'_key': u'foo1', 'value': u'bar1'}
```

#### Start with defining a model

```python
from collector.field import Field
from collector.model import Model

class FooModel(Model):
    value = Field()
    another_value = Field()

```

#### Create a collection instance

```python
from collector.collection import Collection

collection = Collection(projectid='1001', collection='experimental_collection', apikey='sample_api_key')
```

#### Create an instance of the model

```python
fm = FooModel(collection=collection)
```
#### Fetch all available data

```python
for data in fm.execute():
    print data
"""
{'_key': u'foo', 'another_value': u'another_bar', '_ts': 1432160309147, 'value': u'bar'}
{'_key': u'foo1', 'another_value': None, '_ts': 1431989173544, 'value': u'bar1'}
"""
```

#### Fetch particular entry based on **'_key'**

```python
query = fm.select('foo')
foo = query.execute().first()
print foo
"""
{'_key': u'foo', 'another_value': u'another_bar', '_ts': 1432160309147, 'value': u'bar'}
"""

for data in foo.select('foo', 'foo1').execute():
    print data
"""
{'_key': u'foo', 'another_value': u'another_bar', '_ts': 1432160309147, 'value': u'bar'}
{'_key': u'foo1', 'another_value': None, '_ts': 1431989173544, 'value': u'bar1'}
"""
```

#### Update particular entry

```python
foo = fm.select('foo').execute().first()
foo.value = 'modified value'
foo.save()

foo2 = fm.select('foo').execute().first()
print foo2
"""
{'_key': u'foo', 'another_value': u'another_bar', '_ts': 1432160309147, 'value': u'modified value'}
"""
```

#### Create a new entry

```python
new_foo = FooModel(collection, _key='new_foo', value='new value', another_value='another new value')
new_foo.save()
print FooModel(collection).select('new_foo').execute().first()
"""
{'_key': u'new_foo', 'another_value': u'another new value', '_ts': 1432233114144, 'value': u'new value'}
"""

yet_another_foo = new_foo.create(_key='yet_another_foo', value='some value', another_value='some other value?')
yet_another_foo.save()
print FooModel(collection).select('yet_another_foo').execute().first()
"""
{'_key': u'yet_another_foo', 'another_value': u'some other value?', '_ts': 1432233254045, 'value': u'some value'}
"""
```

### Delete an entry

```python

foo2 = FooModel(collection).select('foo2').execute().first()
foo2.delete()

# Raises NoSuchElement
FooModel(collection).select('foo2').execute().first()
```

#### Use prefix & prefixcount

```python
for data in fm.prefix('fo').execute():
    print data
"""
{'_key': u'foo', 'another_value': u'another_bar', '_ts': 1432160309147, 'value': u'modified value'}
{'_key': u'foo1', 'another_value': None, '_ts': 1431989173544, 'value': u'bar1'}
"""

for data in fm.prefix('fo', prefixcount=1).execute():
    print data
"""
{'_key': u'foo', 'another_value': u'another_bar', '_ts': 1432160309147, 'value': u'modified value'}
"""
```

#### Query based on timestamp value

```python
print fm.when(startts=1432160309147).execute().first()
"""
{'_key': u'foo', 'another_value': u'another_bar', '_ts': 1432160309147, 'value': u'modified value'}
"""

print fm.when(endtts=1431989173543).execute().first()
"""
{'_key': u'foo', 'another_value': u'another_bar', '_ts': 1432160309147, 'value': u'modified value'}
"""
```

#### Supports Dict operations

```python
# Set & Get values
foo['another_value'] = 'another modified value'
print foo['another_value']
"""
'another modified value'
""""

# Iterate items
print foo.items()
"""
[('_key', u'foo'), ('another_value', 'another modified value'), ('_ts', 1432160309147), ('value', 'modified value')]
"""

# Delete a Field
del foo['another_value']
foo.save()
print FooModel(collection).select('foo').execute().first()
"""
{'_key': u'foo', '_ts': 1432233732290, 'value': u'modified value'}
"""

# You may set deleted variable again.
foo.another_value = "Hi, i'm back!"
foo.save()
print FooModel(collection).select('foo').execute().first()
"""
{'_key': u'foo', 'another_value': u"Hi, i'm back!", '_ts': 1432233732290, 'value': u'modified value'}
"""

# Aside from Field attributes, you may set & get any item which won't appear in collection.
foo['undeclared'] = 'gonna save?'
print foo['undeclared']
"""
gonna save?
"""
foo.save()
print FooModel(collection).select('foo').execute().first()
"""
{'_key': u'foo', 'another_value': u"Hi, i'm back!", '_ts': 1432233732290, 'value': u'modified value'}
"""
```

#### Limitations

* _key and _ts are immutable model instance variables and cannot be changed.

* A **Field()** attribute cannot be created at runtime because of the fact that python descriptors can not be set to an instance variables at runtime. Hence, if there is missing Field declaration, the relevant field from queried data will be ignored. Because of that very same reason, created variables at runtime (for example by using dict setitem operation), won't be reflected to the collection.
