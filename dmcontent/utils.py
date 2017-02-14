import collections

from jinja2 import Markup, StrictUndefined, TemplateSyntaxError, UndefinedError
from jinja2.sandbox import SandboxedEnvironment
from markdown import markdown
from six import string_types

from .errors import ContentTemplateError


class TemplateField(object):
    def __init__(self, field_value, markdown=None):
        self.source = field_value

        if markdown is None:
            self.markdown = '\n' in field_value
        else:
            self.markdown = markdown

        try:
            self.template = self.make_template(field_value)
        except TemplateSyntaxError as e:
            raise ContentTemplateError(e.message)

    def make_template(self, field_value):
        env = SandboxedEnvironment(autoescape=True, undefined=StrictUndefined)
        template = markdown(field_value, []) if self.markdown else field_value

        return env.from_string(template)

    def render(self, context=None):
        try:
            return Markup(self.template.render(context or {}))
        except UndefinedError as e:
            raise ContentTemplateError(e.message)

    def __eq__(self, other):
        if not isinstance(other, TemplateField):
            return False
        return (self.source == other.source)

    def __repr__(self):
        return '<{}: "{}">'.format(
            self.__class__.__name__,
            self.source.encode('utf-8')
        )


def template_all(item):
    if isinstance(item, string_types):
        return TemplateField(item)
    elif isinstance(item, collections.Sequence):
        return [template_all(i) for i in item]
    elif isinstance(item, collections.Mapping):
        result = {}
        for (key, val) in item.items():
            result[key] = template_all(val)
        return result
    else:
        return item


def drop_followups(question_or_section, data):
    # Remove any follow up answer if the question that requires followup has been answered
    # with a non-followup value

    data = data.copy()

    for question in question_or_section.questions:
        for followup_id, values in question.get('followup', {}).items():
            if data.get(question.id) not in values:
                for field in question_or_section.get_question(followup_id).form_fields:
                    data.pop(field, None)

    return data
