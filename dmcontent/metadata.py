class ContentMetadata:
    """
    A simple reader for framework-related static data. This class performs a similar function to a ContentMessage,
    except it does not parse or render any of the data passed in, so templated messages are not supported.
    """
    def __init__(self, data):
        self._data = data.copy()

    def get(self, key, default=None):
        try:
            return getattr(self, key)
        except AttributeError:
            return default

    def __eq__(self, other):
        if not isinstance(other, ContentMetadata):
            return False
        return self._data == other._data

    def __getattr__(self, key):
        try:
            field = self._data[key]
        except KeyError:
            raise AttributeError(key)

        return self._render(field)

    def _render(self, field):
        if isinstance(field, dict):
            return ContentMetadata(field)
        elif isinstance(field, list):
            return [self._render(i) for i in field]
        else:
            return field

    def __getitem__(self, key):
        return getattr(self, key)

    def __repr__(self):
        return '<{0.__class__.__name__}: data={0._data}>'.format(self)
