from dmcontent.utils import TemplateField


class ContentMessage(object):
    def __init__(self, data, _context=None):
        self._data = data.copy()
        self._context = _context

    def filter(self, context, inplace_allowed: bool = False) -> "ContentMessage":
        message = self if inplace_allowed else ContentMessage(self._data)
        message._context = context

        return message

    def get(self, key, default=None):
        try:
            return getattr(self, key)
        except AttributeError:
            return default

    def __eq__(self, other):
        if not isinstance(other, ContentMessage):
            return False
        return (self._data == other._data) and (self._context == other._context)

    def __getattr__(self, key):
        try:
            field = self._data[key]
        except KeyError:
            raise AttributeError(key)

        return self._render(field)

    def _render(self, field):
        if isinstance(field, TemplateField):
            return field.render(self._context)
        elif isinstance(field, dict):
            return ContentMessage(field, _context=self._context)
        elif isinstance(field, list):
            return [self._render(i) for i in field]
        else:
            return field

    def __getitem__(self, key):
        return getattr(self, key)

    def __repr__(self):
        return '<{0.__class__.__name__}: data={0._data}>'.format(self)
