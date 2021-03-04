# -*- coding: utf-8 -*-

import mock
import pytest
from jinja2 import Environment, Markup

from dmcontent.content_loader import ContentManifest, ContentSection
from dmcontent.errors import ContentTemplateError, ContentNotFoundError
from dmcontent.questions import QuestionSummary
from dmcontent.utils import (
    TemplateField,
    get_option_value,
    try_load_manifest,
    try_load_metadata,
    try_load_messages,
    count_unanswered_questions, LazyDict,
)


class TestTemplateField(object):
    def test_template_field_eq(self):
        assert TemplateField(u'string') == TemplateField(u'string')
        assert not (TemplateField(u'string') == 'string')

    def test_template_field_repr(self):
        assert TemplateField(u'string').__repr__()

    def test_empty_template(self):
        field = TemplateField('')
        assert field.render() == ''

    def test_template_field_with_force_markdown(self):
        field = TemplateField('Hello *world*', markdown=True)
        assert field.render() == '<p class="govuk-body">Hello <em>world</em></p>'

    def test_template_renders_as_markup(self):
        field = TemplateField('simple template')
        assert isinstance(field.render(), Markup)

    def test_template_without_template_tags(self):
        field = TemplateField('simple template')
        assert field.render() == 'simple template'

    def test_unicode_characters_in_template(self):
        field = TemplateField(u'\u00a3simple template')
        assert field.render() == u'£simple template'

    def test_html_tags_in_template_are_not_escaped(self):
        field = TemplateField(u'<span>simple&nbsp;template</span>')
        assert field.render() == u'<span>simple&nbsp;template</span>'

    def test_template_with_context(self):
        field = TemplateField(u'template {{ name }}')
        assert field.render({'name': 'context'}) == u'template context'

    def test_template_with_conditions(self):
        field = TemplateField(u"{% if name == 'context' %}template {{ name }}{% endif %}")
        assert field.render({'name': 'context'}) == u'template context'

    def test_undefined_template_variables_raise_an_error(self):
        field = TemplateField(u'template {{ name }}')

        with pytest.raises(ContentTemplateError):
            field.render()

    def test_unused_template_variables_are_ignored(self):
        field = TemplateField(u'template {{ name }}')

        assert field.render({'name': 'context', 'lot': 'lot'}) == u'template context'

    def test_unicode_characters_in_template_context(self):
        field = TemplateField(u'template {{ name }}')
        assert field.render({'name': u'\u00a3context'}) == u'template £context'

    def test_html_tags_in_template_context_are_escaped(self):
        field = TemplateField(u'template {{ name }}')
        assert field.render(
            {'name': '<span>context&nbsp;</span>'}
        ) == u'template &lt;span&gt;context&amp;nbsp;&lt;/span&gt;'

    def test_template_tags_in_template_context_are_not_evaluated(self):
        field = TemplateField(u'template {{ name }}')
        assert field.render(
            {'name': '{{ other }}'}
        ) == u'template {{ other }}'

    def test_fields_are_processed_with_markdown(self):
        field = TemplateField(u'# Title\n* Hello\n* Markdown')

        assert field.render() == """<h1>Title</h1>
<ul class="govuk-list govuk-list--bullet">
<li>Hello</li>
<li>Markdown</li>
</ul>"""

    def test_simple_strings_are_not_wrapped_in_paragraph_tags(self):
        field = TemplateField(u'Title string')

        assert field.render() == 'Title string'

    def test_markdown_strings_govuk_classes(self):
        field = TemplateField(
            u'##A Heading\n\n'
            u'Some paragraph\n\n'
            u' * Some\n'
            u' * List\n\n'
            u'And\n\n'
            u'1. Some other\n'
            u'2. [Ordered](http://example.com)\n'
            u'3. List & such'
        )

        assert field.render() == """<h2 class="govuk-heading-m">A Heading</h2>
<p class="govuk-body">Some paragraph</p>
<ul class="govuk-list govuk-list--bullet">
<li>Some</li>
<li>List</li>
</ul>
<p class="govuk-body">And</p>
<ol class="govuk-list govuk-list--number">
<li>Some other</li>
<li><a class="govuk-link" href="http://example.com">Ordered</a></li>
<li>List &amp; such</li>
</ol>"""

    def test_jinja_markdown_errors_raise_an_exception(self):
        with pytest.raises(ContentTemplateError):
            TemplateField(u'Title:\nnumber {{ number*2*5 }}')

    def test_markdown_characters_in_jinja_tags(self):
        assert TemplateField(u'Title:\nnumber {{ number._value }}')
        assert TemplateField(u'Title:\nnumber {{ number["value"] }}')
        assert TemplateField(u'Title:\nnumber {{ number|join(".") }}')
        assert TemplateField(u"Title:\n{% if name == 'context' %}template {{ name }}{% endif %}")


class TestTemplateFieldsInTemplate(object):
    def test_html_in_field_variables_is_escaped(self):
        env = Environment(autoescape=True)
        template_string = "This is a {{ name }} template"
        rendered_field = TemplateField(template_string).render({'name': '<em>context</em>'})
        final_template = env.from_string('{{ rendered_field }}').render({'rendered_field': rendered_field})

        assert final_template == 'This is a &lt;em&gt;context&lt;/em&gt; template'

    def test_html_in_content_is_not_escaped(self):
        env = Environment(autoescape=True)
        template_string = "This *is* a {{ name }} <em>template</em>\n"
        rendered_field = TemplateField(template_string).render({'name': 'context'})
        final_template = env.from_string('{{ rendered_field }}').render({'rendered_field': rendered_field})

        assert final_template == '<p class="govuk-body">This <em>is</em> a context <em>template</em></p>'

    def test_jinja_in_field_variables_is_not_evaluated(self):
        env = Environment(autoescape=True)
        template_string = "This is a {{ name }} template"
        rendered_field = TemplateField(template_string).render({'name': '{{ context }}'})
        final_template = env.from_string('{{ rendered_field }}').render({'rendered_field': rendered_field})

        assert final_template == 'This is a {{ context }} template'

    def test_html_in_field_variables_is_escaped_with_safe(self):
        env = Environment(autoescape=True)
        template_string = "This is a {{ name }} template"
        rendered_field = TemplateField(template_string).render({'name': '<em>context</em>'})
        final_template = env.from_string('{{ rendered_field|safe }}').render({'rendered_field': rendered_field})

        assert final_template == 'This is a &lt;em&gt;context&lt;/em&gt; template'

    def test_html_in_content_is_not_escaped_with_safe(self):
        env = Environment(autoescape=True)
        template_string = "This *is* a {{ name }} <em>template</em>\n"
        rendered_field = TemplateField(template_string).render({'name': 'context'})
        final_template = env.from_string('{{ rendered_field|safe }}').render({'rendered_field': rendered_field})

        assert final_template == '<p class="govuk-body">This <em>is</em> a context <em>template</em></p>'

    def test_jinja_in_field_variables_is_not_evaluated_with_safe(self):
        env = Environment(autoescape=True)
        template_string = "This is a {{ name }} template"
        rendered_field = TemplateField(template_string).render({'name': '{{ context }}'})
        final_template = env.from_string('{{ rendered_field|safe }}').render({'rendered_field': rendered_field})

        assert final_template == 'This is a {{ context }} template'


def test_get_option_value():
    option_value_no_label = {
        'value': 'somevalue',
    }
    option_label_no_value = {
        'label': 'somelabel',
    }
    option_label_and_value = {
        'value': 'somevalue',
        'label': 'somelabel',
    }

    assert get_option_value(option_value_no_label) == 'somevalue'
    assert get_option_value(option_label_no_value) == 'somelabel'
    assert get_option_value(option_label_and_value) == 'somevalue'


class TestTryLoadManifest:
    FRAMEWORK_DATA = {'slug': 'framework'}
    QUESTION_SET = 'services'
    MANIFEST = 'example'

    def setup(self):
        self.content_loader_mock = mock.Mock()
        self.application_mock = mock.Mock()

    def test_content_loader_asked_to_load_manifest(self):
        try_load_manifest(self.content_loader_mock,
                          self.application_mock,
                          TestTryLoadManifest.FRAMEWORK_DATA,
                          TestTryLoadManifest.QUESTION_SET,
                          TestTryLoadManifest.MANIFEST
                          )

        assert self.content_loader_mock.load_manifest.call_args_list == [
            mock.call(TestTryLoadManifest.FRAMEWORK_DATA['slug'],
                      TestTryLoadManifest.QUESTION_SET,
                      TestTryLoadManifest.MANIFEST)
        ]
        assert self.application_mock.logger.info.called is False

    def test_info_log_generated_on_content_not_found(self):
        self.content_loader_mock.load_manifest.side_effect = ContentNotFoundError()

        try_load_manifest(self.content_loader_mock,
                          self.application_mock,
                          TestTryLoadManifest.FRAMEWORK_DATA,
                          TestTryLoadManifest.QUESTION_SET,
                          TestTryLoadManifest.MANIFEST
                          )

        assert self.content_loader_mock.load_manifest.call_args_list == [
            mock.call(TestTryLoadManifest.FRAMEWORK_DATA['slug'],
                      TestTryLoadManifest.QUESTION_SET,
                      TestTryLoadManifest.MANIFEST)
        ]

        assert self.application_mock.logger.info.call_args_list == [
            mock.call('Could not load {}.{} manifest for {}'.format(
                TestTryLoadManifest.QUESTION_SET,
                TestTryLoadManifest.MANIFEST,
                TestTryLoadManifest.FRAMEWORK_DATA['slug']))
        ]


class TestTryLoadMetadata:
    FRAMEWORK_DATA = {'slug': 'framework'}
    METADATA = ['example']

    def setup(self):
        self.content_loader_mock = mock.Mock()
        self.application_mock = mock.Mock()

    def test_content_loader_asked_to_load_metadata(self):
        try_load_metadata(self.content_loader_mock,
                          self.application_mock,
                          TestTryLoadMetadata.FRAMEWORK_DATA,
                          TestTryLoadMetadata.METADATA
                          )

        assert self.content_loader_mock.load_metadata.call_args_list == [
            mock.call(TestTryLoadMetadata.FRAMEWORK_DATA['slug'],
                      TestTryLoadMetadata.METADATA)
        ]
        assert self.application_mock.logger.info.called is False

    def test_info_log_generated_on_content_not_found(self):
        self.content_loader_mock.load_metadata.side_effect = ContentNotFoundError()

        try_load_metadata(self.content_loader_mock,
                          self.application_mock,
                          TestTryLoadMetadata.FRAMEWORK_DATA,
                          TestTryLoadMetadata.METADATA
                          )

        assert self.content_loader_mock.load_metadata.call_args_list == [
            mock.call(TestTryLoadMetadata.FRAMEWORK_DATA['slug'],
                      TestTryLoadMetadata.METADATA)
        ]

        assert self.application_mock.logger.info.call_args_list == [
            mock.call("Could not load '{}' metadata for {}".format(
                TestTryLoadMetadata.METADATA,
                TestTryLoadMetadata.FRAMEWORK_DATA['slug']))
        ]


class TestTryLoadMessages:
    FRAMEWORK_DATA = {'slug': 'framework'}
    MESSAGES = ['example']

    def setup(self):
        self.content_loader_mock = mock.Mock()
        self.application_mock = mock.Mock()

    def test_content_loader_asked_to_load_messages(self):
        try_load_messages(self.content_loader_mock,
                          self.application_mock,
                          TestTryLoadMessages.FRAMEWORK_DATA,
                          TestTryLoadMessages.MESSAGES
                          )

        assert self.content_loader_mock.load_messages.call_args_list == [
            mock.call(TestTryLoadMessages.FRAMEWORK_DATA['slug'],
                      TestTryLoadMessages.MESSAGES)
        ]
        assert self.application_mock.logger.info.called is False

    def test_info_log_generated_on_content_not_found(self):
        self.content_loader_mock.load_messages.side_effect = ContentNotFoundError()

        try_load_messages(self.content_loader_mock,
                          self.application_mock,
                          TestTryLoadMessages.FRAMEWORK_DATA,
                          TestTryLoadMessages.MESSAGES
                          )

        assert self.content_loader_mock.load_messages.call_args_list == [
            mock.call(TestTryLoadMessages.FRAMEWORK_DATA['slug'],
                      TestTryLoadMessages.MESSAGES)
        ]

        assert self.application_mock.logger.info.call_args_list == [
            mock.call("Could not load '{}' messages for {}".format(
                TestTryLoadMessages.MESSAGES,
                TestTryLoadMessages.FRAMEWORK_DATA['slug']))
        ]


def test_count_unanswered_questions():
    mock_content_manifest = mock.create_autospec(ContentManifest, instance=True)
    mock_content_manifest.__iter__.side_effect = lambda: (
        mock.create_autospec(ContentSection, instance=True, questions=[
            mock.create_autospec(QuestionSummary, instance=True, answer_required=answer_required, value=value)
            for answer_required, value in questions
        ]) for questions in (
            (
                (True, ""),
                (False, "123"),
                (True, ["321"]),
            ), (
                (False, None),
                (False, []),
                (True, "abc"),
                (True, "yes"),
                (True, "no"),
                (True, None),
                (False, "2020-01-01T01:01:01Z"),
            ), (
                (False, []),
            ),
        )
    )

    assert count_unanswered_questions(mock_content_manifest) == (6, 3)


class TestLazyDict:
    def setup(self):
        self.callable_mock = mock.Mock()

    def test_stores_callables(self):
        LazyDict(test=self.callable_mock)

        assert self.callable_mock.call_count == 0

    def test_calls_lazily(self):
        test_dict = LazyDict(test=self.callable_mock)

        test_dict.get("test")

        assert self.callable_mock.call_count == 1

    def test_caches_result(self):
        test_dict = LazyDict(test=self.callable_mock)

        test_dict.get("test")
        test_dict.get("test")

        assert self.callable_mock.call_count == 1

    def test_stores_non_callables(self):
        test_dict = LazyDict(test="test")

        assert test_dict.get("test") == "test"
