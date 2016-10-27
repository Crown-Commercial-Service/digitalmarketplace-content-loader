from jinja2 import StrictUndefined
from jinja2.sandbox import SandboxedEnvironment


class TemplateField(object):
    def __init__(self, field_value):
        env = SandboxedEnvironment(autoescape=True, undefined=StrictUndefined)
        self._field_value = field_value
        self.template = env.from_string(field_value)
        self.context = {}

    def render(self):
        return self.template.render(self.context)

    def __eq__(self, other):
        if not isinstance(other, TemplateField):
            return False
        return (self._field_value == other._field_value) and (self.context == other.context)

    def __repr__(self):
        return '<{0.__class__.__name__}: "{0._field_value}", context={0.context}>'.format(self)
