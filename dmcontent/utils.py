from jinja2 import Markup, StrictUndefined, TemplateSyntaxError, UndefinedError
from jinja2.sandbox import SandboxedEnvironment
from markdown import markdown

from .errors import ContentTemplateError


class TemplateField(object):
    def __init__(self, field_value):
        self._field_value = field_value
        try:
            self.template = self.make_template(field_value)
        except TemplateSyntaxError as e:
            raise ContentTemplateError(e.message)

    def make_template(self, field_value):
        env = SandboxedEnvironment(autoescape=True, undefined=StrictUndefined)
        if '\n' in field_value:
            template = markdown(field_value, [])
        else:
            template = field_value

        return env.from_string(template)

    def render(self, context=None):
        try:
            return Markup(self.template.render(context or {}))
        except UndefinedError as e:
            raise ContentTemplateError(e.message)

    def __eq__(self, other):
        if not isinstance(other, TemplateField):
            return False
        return (self._field_value == other._field_value)

    def __repr__(self):
        return '<{0.__class__.__name__}: "{0._field_value}">'.format(self)
