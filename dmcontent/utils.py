from jinja2 import StrictUndefined, UndefinedError
from jinja2.sandbox import SandboxedEnvironment

from .errors import ContentTemplateError


class TemplateField(object):
    def __init__(self, field_value):
        env = SandboxedEnvironment(autoescape=True, undefined=StrictUndefined)
        self._field_value = field_value
        self.template = env.from_string(field_value)

    def render(self, context=None):
        try:
            return self.template.render(context or {})
        except UndefinedError as e:
            raise ContentTemplateError(e.message)

    def __eq__(self, other):
        if not isinstance(other, TemplateField):
            return False
        return (self._field_value == other._field_value)

    def __repr__(self):
        return '<{0.__class__.__name__}: "{0._field_value}">'.format(self)
