import json
from io import StringIO


class JsonLinesIterator(object):
    def __init__(self, data):
        data = unicode(data) if data else None
        self.sio = StringIO(data)

    def __iter__(self):
        for line in self.sio:
            yield json.loads(line)

    @staticmethod
    def serialize(data):
        if isinstance(data, list):
            return '\n'.join([json.dumps(line) for line in data])
        else:
            return json.dumps(data)