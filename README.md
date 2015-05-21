# Collector
An ORM library for Scrapinghub Collections API which uses HTTP requests to communicate with data storage. 

For more about Collections API visit http://doc.scrapinghub.com/collections.html

## Examples
Say, we have collection with following data:

```python
{'_key': u'foo', 'another_value': u'another_bar', 'value': u'bar'}
{'_key': u'foo1', 'value': u'bar1'}
```

#### Define a model

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

#### Create instance of the model

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

#### Fetch particular data based on **'_key'**

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

#### Update particular data

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
print fm.when(starts=1432160309147).execute().first()
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
foo['another_value'] = 'another modified value'
print foo['another_value']
"""
'another modified value'
""""

print foo.items()
"""
[('_key', u'foo'), ('another_value', 'another modified value'), ('_ts', 1432160309147), ('value', 'modified value')]
"""
```

#### Limitations

* _key and _ts are immutable model instance variables and cannot be changed.

* A **Field()** attribute cannot be created at runtime (because python descriptors could not be set to instance variables). Hence, if there is missing Field declaration, the relevant field from queried data will be ignored. Because of that reason, created variables at runtime (for example by using dict setitem operation), won't be reflected to the collection.
