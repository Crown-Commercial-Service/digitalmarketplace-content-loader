import pytest
from jinja2 import UndefinedError

from dmcontent.questions import Question
from dmcontent.content_loader import ContentSection


class TestFilterContentSection(object):
    def test_fields_without_template_tags_are_unchanged(self):
        section = ContentSection(
            slug='section',
            name='Section',
            description='just a string',
            editable=False,
            edit_questions=False,
            questions=[Question({})]
        )

        assert section.filter({}).name == 'Section'
        assert section.filter({}).description == 'just a string'

    def test_question_fields_without_template_tags_are_unchanged(self):
        section = ContentSection(
            slug='section',
            name='Section',
            editable=False,
            edit_questions=False,
            questions=[Question({'name': 'Question'})]
        )

        assert section.filter({}).questions[0].name == 'Question'

    def test_not_all_fields_are_templated(self):
        section = ContentSection(
            slug='# {{ section }}',
            name='Section',
            editable=False,
            edit_questions=False,
            questions=[Question({})]
        )

        assert section.filter({}).slug == '# {{ section }}'

    def test_missing_context_variable_raises_an_error(self):
        section = ContentSection(
            slug='section',
            name='Section {{ name }}',
            editable=False,
            edit_questions=False,
            questions=[Question({})]
        )

        with pytest.raises(UndefinedError):
            section.filter({}).name

    def test_section_name_is_templated(self):
        section = ContentSection(
            slug='section',
            name='Section {{ name }}',
            editable=False,
            edit_questions=False,
            questions=[Question({})]
        )

        assert section.filter({'name': 'one'}).name == 'Section one'

    def test_unused_context_variables_are_ignored(self):
        section = ContentSection(
            slug='section',
            name='Section {{ name }}',
            editable=False,
            edit_questions=False,
            questions=[Question({})]
        )

        assert section.filter({'name': 'one', 'name2': 'ignored'}).name == 'Section one'

    def test_section_description_is_templated(self):
        section = ContentSection(
            slug='section',
            name='Section one',
            editable=False,
            edit_questions=False,
            questions=[Question({})],
            description="This is the {{ name }} section"
        )

        assert section.filter({'name': 'first'}).description == 'This is the first section'

    def test_section_description_is_not_set(self):
        section = ContentSection(
            slug='section',
            name='Section one',
            editable=False,
            edit_questions=False,
            questions=[Question({})],
            description=None
        )

        assert section.filter({}).description is None

    def test_get_section_description_before_filter_raises_error(self):
        section = ContentSection(
            slug='section',
            name='Section one',
            editable=False,
            edit_questions=False,
            questions=[Question({})],
            description="description for {% if lot == 'digital-specialists' %}specialists{% else %}outcomes{% endif %}"
        )

        with pytest.raises(TypeError):
            section.description

    def test_filtering_a_section_with_a_description_template(self):
        section = ContentSection(
            slug='section',
            name='Section one',
            editable=False,
            edit_questions=False,
            questions=[Question({})],
            description="description for {% if lot == 'digital-specialists' %}specialists{% else %}outcomes{% endif %}"
        )

        assert section.filter({"lot": "digital-specialists"}).description == "description for specialists"
        assert section.filter({"lot": "digital-outcomes"}).description == "description for outcomes"
