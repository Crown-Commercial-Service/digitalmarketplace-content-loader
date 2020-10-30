import collections
import typing

from jinja2 import Markup, StrictUndefined, TemplateSyntaxError, UndefinedError
from markdown import Markdown

from dmutils.jinja2_environment import DMSandboxedEnvironment
from dmcontent.errors import ContentNotFoundError

from .errors import ContentTemplateError
from .markdown import GOVUKFrontendExtension


if typing.TYPE_CHECKING:
    from dmcontent.content_loader import ContentManifest


# jinja's environments are threadsafe (unless you explicitly mutate them during operation, which is not recommended),
# so it should be safe to keep this as a shared global
template_environment = DMSandboxedEnvironment(autoescape=True, undefined=StrictUndefined)


class _ImmutableTemplateProxy:
    """
        A heavily abbreviated proxy for a jinja Template that should help ensure (effective) immutability and
        threadsafety
    """
    __slots__ = ("render",)

    def __init__(self, template):
        # instead of keeping a reference to the template on the instance where external code could be e.g. inadvertantly
        # calling mutating methods on it, seal it in the closure of a function which itself will _become_ our render
        # "method".
        self.render = lambda *args, **kwargs: template.render(*args, **kwargs)

    def __deepcopy__(self, memo):
        # we're (effectively) immutable.
        return self


class TemplateField(object):
    markdown_instance = Markdown(extensions=[GOVUKFrontendExtension()])

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
        template = self.markdown_instance.convert(field_value) if self.markdown else field_value

        return _ImmutableTemplateProxy(template_environment.from_string(template))

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
    if isinstance(item, str):
        return TemplateField(item)
    elif isinstance(item, collections.abc.Sequence):
        return [template_all(i) for i in item]
    elif isinstance(item, collections.abc.Mapping):
        result = {}
        for (key, val) in item.items():
            result[key] = template_all(val)
        return result
    else:
        return item


def drop_followups(question_or_section, data, nested=False):
    """Remove any follow up answer if the lead-in question value doesn't require a follow up.

    For nested questions (eg questions insidea a dynamic list array) we remove the question field
    completely, since the top-level data key will be replaced anyway.

    For multiquestions that are serialized to separate top-level keys we set the follow-up value
    to `None`, so that it's replaced if the question was previously answered with a follow-up.

    """

    data = data.copy()

    for question in question_or_section.questions:
        for followup_id, values in question.get('followup', {}).items():
            question_data = data.get(question.id)
            if not isinstance(question_data, list):
                question_data = [question_data]

            if not set(question_data) & set(values):
                for field in question_or_section.get_question(followup_id).form_fields:
                    if nested:
                        data.pop(field, None)
                    else:
                        data[field] = None

    return data


def get_option_value(option):
    """
    An option in a Checkboxes or CheckboxTree question is a dict, but we need to treat their
    contents in consistent ways, e.g. when getting the value to be persisted in the API.
    :param option: dict from a Question's list of options
    :return: string value to be persisted
    """
    return option.get('value') or option['label']


def try_load_manifest(content_loader, application, data, question_set, manifest):
    try:
        content_loader.load_manifest(data['slug'], question_set, manifest)

    except ContentNotFoundError:
        application.logger.info(
            "Could not load {}.{} manifest for {}".format(question_set, manifest, data['slug'])
        )


def try_load_metadata(content_loader, application, data, metadata):
    try:
        content_loader.load_metadata(data['slug'], metadata)

    except ContentNotFoundError:
        application.logger.info(
            "Could not load '{}' metadata for {}".format(metadata, data['slug'])
        )


def try_load_messages(content_loader, application, data, messages):
    try:
        content_loader.load_messages(data['slug'], messages)

    except ContentNotFoundError:
        application.logger.info(
            "Could not load '{}' messages for {}".format(messages, data['slug'])
        )


def count_unanswered_questions(service_attributes: "ContentManifest") -> typing.Tuple[int, int]:
    """
        Given a "summary" ContentManifest, returns a tuple of integers representing
        respectively the number of unanswered-and-required questions and the number
        of unanswered-but-optional questions.
    """
    unanswered_required, unanswered_optional = 0, 0
    for section in service_attributes:
        for question in section.questions:
            if question.answer_required:
                unanswered_required += 1
            elif question.value in ('', [], None,):
                unanswered_optional += 1

    return unanswered_required, unanswered_optional
