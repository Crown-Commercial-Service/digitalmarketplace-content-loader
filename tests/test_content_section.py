import pytest
from jinja2 import UndefinedError

from dmcontent.utils import TemplateField
from dmcontent.questions import Question, Multiquestion
from dmcontent.content_loader import ContentSection
from dmcontent import ContentTemplateError


class TestFilterContentSection(object):
    def test_fields_without_template_tags_are_unchanged(self):
        section = ContentSection(
            slug='section',
            name=TemplateField('Section'),
            description=TemplateField('just a string'),
            editable=False,
            edit_questions=False,
            questions=[Question({})]
        )

        assert section.filter({}).name == 'Section'
        assert section.filter({}).description == 'just a string'

    def test_question_fields_without_template_tags_are_unchanged(self):
        section = ContentSection(
            slug='section',
            name=TemplateField('Section'),
            editable=False,
            edit_questions=False,
            questions=[Question({'name': 'Question'})]
        )

        assert section.filter({}).questions[0].name == 'Question'

    def test_not_all_fields_are_templated(self):
        section = ContentSection(
            slug='# {{ section }}',
            name=TemplateField('Section'),
            editable=False,
            edit_questions=False,
            questions=[Question({})]
        )

        assert section.filter({}).slug == '# {{ section }}'

    def test_missing_context_variable_raises_an_error(self):
        section = ContentSection(
            slug='section',
            name=TemplateField('Section {{ name }}'),
            editable=False,
            edit_questions=False,
            questions=[Question({})]
        )

        with pytest.raises(ContentTemplateError):
            section.filter({}).name

    def test_section_name_is_templated(self):
        section = ContentSection(
            slug='section',
            name=TemplateField('Section {{ name }}'),
            editable=False,
            edit_questions=False,
            questions=[Question({})]
        )

        assert section.filter({'name': 'one'}).name == 'Section one'

    def test_unused_context_variables_are_ignored(self):
        section = ContentSection(
            slug='section',
            name=TemplateField('Section {{ name }}'),
            editable=False,
            edit_questions=False,
            questions=[Question({})]
        )

        assert section.filter({'name': 'one', 'name2': 'ignored'}).name == 'Section one'

    def test_section_description_is_templated(self):
        section = ContentSection(
            slug='section',
            name=TemplateField('Section one'),
            editable=False,
            edit_questions=False,
            questions=[Question({})],
            description=TemplateField("This is the {{ name }} section")
        )

        assert section.filter({'name': 'first'}).description == 'This is the first section'

    def test_section_description_is_not_set(self):
        section = ContentSection(
            slug='section',
            name=TemplateField('Section one'),
            editable=False,
            edit_questions=False,
            questions=[Question({})]
        )

        assert section.filter({}).description is None

    def test_get_templatable_section_attributes_calls_render(self):
        section = ContentSection(
            slug='section',
            name=TemplateField('{% if True %}Section one{% else %}Section two{% endif %}'),
            editable=False,
            edit_questions=False,
            questions=[Question({})],
            description=TemplateField(
                "description for {% if lot == 'digital-specialists' %}specialists{% else %}outcomes{% endif %}"
            )
        )

        assert section.name == 'Section one'
        with pytest.raises(ContentTemplateError):
            section.description

        assert section.slug == 'section'

    def test_copying_section_preserves_value_of_filtered_attribute(self):
        section = ContentSection(
            slug='section',
            name=TemplateField('Section'),
            editable=False,
            edit_questions=False,
            questions=[Question({'name': 'Question'})]
        ).filter({'context': 'context1'})
        assert section._context == {'context': 'context1'}

        copied_section = section.copy()
        assert copied_section._context == section._context

    def test_getting_a_multiquestion_as_a_section_preserves_value_of_filtered_attribute(self):
        multiquestion_data = {
            "id": "example",
            "slug": "example",
            "question": "Example question",
            "type": "multiquestion",
            "questions": [
                {
                    "id": "example2",
                    "type": "text",
                },
                {
                    "id": "example3",
                    "type": "number",
                }
            ]
        }

        section = ContentSection(
            slug='section',
            name=TemplateField('Section'),
            editable=False,
            edit_questions=False,
            questions=[Multiquestion(multiquestion_data)]
        )

        assert section.get_question_as_section('example')._context is None
        assert section.filter(
            {'context': 'context1'}
        ).get_question_as_section('example')._context == {'context': 'context1'}

    def test_filtering_a_section_with_a_description_template(self):
        section = ContentSection(
            slug='section',
            name=TemplateField('Section one'),
            editable=False,
            edit_questions=False,
            questions=[Question({})],
            description=TemplateField(
                "description for {% if lot == 'digital-specialists' %}specialists{% else %}outcomes{% endif %}"
            )
        )

        assert section.filter({"lot": "digital-specialists"}).description == "description for specialists"
        assert section.filter({"lot": "digital-outcomes"}).description == "description for outcomes"
