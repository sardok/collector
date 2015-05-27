from collector.exceptions import NoSuchElement


class QueryResult(object):
    """ Contains data from collection database as a result of query execution.

    This class is Iterable and uses collection's iterator class to process
    the result.
    """
    def __init__(self, model, result):
        self.model = model
        self.result = result

    def __iter__(self):
        collection = self.model.collection
        for data in collection.iterator_cls(self.result):
            # Create a new model instance
            model = self.model.create(**data)
            yield model

    def first(self):
        """ Returns first data of the result.

        Raises NoSuchElement if query returns empty result.
        """
        try:
            return next(iter(self))
        except StopIteration:
            raise NoSuchElement

    def all(self):
        """ Returns list of all result. Normally the iteration is lazy, this
         function creates list from the lazy iteration.

         Equivalent of list(iter(query_result))
        """
        return list(iter(self))
