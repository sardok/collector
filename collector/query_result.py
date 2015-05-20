from collector.exceptions import NoSuchElement


class QueryResult(object):
    def __init__(self, model, result):
        self.model = model
        self.result = result

    def __iter__(self):
        collection = self.model.collection
        for data in collection.iterator_cls(self.result):
            # Create a new model instance
            model = type(self.model)(collection=collection, **data)
            yield model

    def first(self):
        try:
            return next(iter(self))
        except StopIteration:
            raise NoSuchElement

    def all(self):
        return list(iter(self))
