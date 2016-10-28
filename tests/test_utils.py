# -*- coding: utf-8 -*-

import pytest

from dmcontent.errors import ContentTemplateError
from dmcontent.utils import TemplateField


class TestTemplateField(object):
    def test_empty_template(self):
        field = TemplateField('')
        assert field.render() == ''

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

        assert field.render() == '<h1>Title</h1>\n<ul>\n<li>Hello</li>\n<li>Markdown</li>\n</ul>'

    def test_simple_strings_are_not_wrapped_in_paragraph_tags(self):
        field = TemplateField(u'Title string')

        assert field.render() == 'Title string'

    def test_jinja_markdown_errors_raise_an_exception(self):
        with pytest.raises(ContentTemplateError):
            TemplateField(u'Title:\nnumber {{ number*2*5 }}')

    def test_markdown_characters_in_jinja_tags(self):
        assert TemplateField(u'Title:\nnumber {{ number._value }}')
        assert TemplateField(u'Title:\nnumber {{ number["value"] }}')
        assert TemplateField(u'Title:\nnumber {{ number|join(".") }}')
        assert TemplateField(u"Title:\n{% if name == 'context' %}template {{ name }}{% endif %}")
