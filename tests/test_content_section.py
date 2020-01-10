import pytest

from werkzeug.datastructures import MultiDict

from dmcontent.utils import TemplateField
from dmcontent.questions import Question, Multiquestion
from dmcontent.content_loader import ContentSection
from dmcontent import ContentTemplateError


class TestFilterContentSection(object):
    @pytest.mark.parametrize("filter_inplace_allowed", (False, True,))
    def test_fields_without_template_tags_are_unchanged(self, filter_inplace_allowed):
        section = ContentSection(
            slug='section',
            name=TemplateField('Section'),
            description=TemplateField('just a string'),
            prefill=True,
            editable=False,
            edit_questions=False,
            questions=[Question({})]
        )

        sf = section.filter({}, inplace_allowed=filter_inplace_allowed)

        assert sf.name == 'Section'
        assert sf.description == 'just a string'
        assert sf.prefill is True

    @pytest.mark.parametrize("filter_inplace_allowed", (False, True,))
    def test_question_fields_without_template_tags_are_unchanged(self, filter_inplace_allowed):
        section = ContentSection(
            slug='section',
            name=TemplateField('Section'),
            prefill=False,
            editable=False,
            edit_questions=False,
            questions=[Question({'name': 'Question'})]
        )

        assert section.filter({}, inplace_allowed=filter_inplace_allowed).questions[0].name == 'Question'

    @pytest.mark.parametrize("filter_inplace_allowed", (False, True,))
    def test_not_all_fields_are_templated(self, filter_inplace_allowed):
        section = ContentSection(
            slug='# {{ section }}',
            name=TemplateField('Section'),
            prefill=True,
            editable=False,
            edit_questions=False,
            questions=[Question({})]
        )

        assert section.filter({}, inplace_allowed=filter_inplace_allowed).slug == '# {{ section }}'

    @pytest.mark.parametrize("filter_inplace_allowed", (False, True,))
    def test_missing_context_variable_raises_an_error(self, filter_inplace_allowed):
        section = ContentSection(
            slug='section',
            name=TemplateField('Section {{ name }}'),
            prefill=False,
            editable=False,
            edit_questions=False,
            questions=[Question({})]
        )

        with pytest.raises(ContentTemplateError):
            section.filter({}, inplace_allowed=filter_inplace_allowed).name

    @pytest.mark.parametrize("filter_inplace_allowed", (False, True,))
    def test_section_name_is_templated(self, filter_inplace_allowed):
        section = ContentSection(
            slug='section',
            name=TemplateField('Section {{ name }}'),
            prefill=True,
            editable=False,
            edit_questions=False,
            questions=[Question({})]
        )

        assert section.filter({'name': 'one'}, inplace_allowed=filter_inplace_allowed).name == 'Section one'

    @pytest.mark.parametrize("filter_inplace_allowed", (False, True,))
    def test_unused_context_variables_are_ignored(self, filter_inplace_allowed):
        section = ContentSection(
            slug='section',
            name=TemplateField('Section {{ name }}'),
            prefill=True,
            editable=False,
            edit_questions=False,
            questions=[Question({})]
        )

        assert section.filter(
            {'name': 'one', 'name2': 'ignored'},
            inplace_allowed=filter_inplace_allowed,
        ).name == 'Section one'

    @pytest.mark.parametrize("filter_inplace_allowed", (False, True,))
    def test_section_description_is_templated(self, filter_inplace_allowed):
        section = ContentSection(
            slug='section',
            name=TemplateField('Section one'),
            prefill=False,
            editable=False,
            edit_questions=False,
            questions=[Question({})],
            description=TemplateField("This is the {{ name }} section")
        )

        assert section.filter(
            {'name': 'first'},
            inplace_allowed=filter_inplace_allowed,
        ).description == 'This is the first section'

    @pytest.mark.parametrize("filter_inplace_allowed", (False, True,))
    def test_section_description_is_not_set(self, filter_inplace_allowed):
        section = ContentSection(
            slug='section',
            name=TemplateField('Section one'),
            prefill=False,
            editable=False,
            edit_questions=False,
            questions=[Question({})]
        )

        assert section.filter({}, inplace_allowed=filter_inplace_allowed).description is None

    def test_get_templatable_section_attributes_calls_render(self):
        section = ContentSection(
            slug='section',
            name=TemplateField('{% if True %}Section one{% else %}Section two{% endif %}'),
            prefill=True,
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

    @pytest.mark.parametrize("filter_inplace_allowed", (False, True,))
    def test_copying_section_preserves_value_of_context_attribute(self, filter_inplace_allowed):
        section = ContentSection(
            slug='section',
            name=TemplateField('Section'),
            prefill=False,
            editable=False,
            edit_questions=False,
            questions=[Question({'name': 'Question'})]
        ).filter({'context': 'context1'}, inplace_allowed=filter_inplace_allowed)
        assert section._context == {'context': 'context1'}

        copied_section = section.copy()
        assert copied_section._context == section._context
        assert copied_section.prefill is False
        assert copied_section.editable is False

    def test_is_empty(self):
        questions = [
            Question({'id': 'q1', 'name': 'q1', 'type': 'unknown'}),
            Question({'id': 'q2', 'name': 'q2', 'type': 'unknown'})
        ]  # note that id and type are required as this function indirectly calls QuestionSummary.value

        section = ContentSection(
            slug='section',
            name=TemplateField('Section'),
            prefill=False,
            editable=False,
            edit_questions=False,
            questions=questions
        )
        answered = section.summary({'q1': 'a1', 'q2': 'a2'})
        assert not answered.is_empty
        half_answered = section.summary({'q1': 'a1', 'q2': ''})
        assert not half_answered.is_empty
        not_answered = section.summary({'q1': '', 'q2': ''})
        assert not_answered.is_empty

    @pytest.mark.parametrize("filter_inplace_allowed", (False, True,))
    def test_getting_a_multiquestion_as_a_section_preserves_value_of_context_attribute(self, filter_inplace_allowed):
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
            prefill=True,
            editable=False,
            edit_questions=False,
            questions=[Multiquestion(multiquestion_data)]
        )

        assert section.get_question_as_section('example')._context is None
        assert section.filter(
            {'context': 'context1'},
            inplace_allowed=filter_inplace_allowed,
        ).get_question_as_section('example')._context == {'context': 'context1'}

    @pytest.mark.parametrize("filter_inplace_allowed", (False, True,))
    @pytest.mark.parametrize("lot,expected_description", (
        ("digital-specialists", "description for specialists",),
        ("digital-outcomes", "description for outcomes",),
    ))
    def test_filtering_a_section_with_a_description_template(self, filter_inplace_allowed, lot, expected_description):
        section = ContentSection(
            slug='section',
            name=TemplateField('Section one'),
            prefill=False,
            editable=False,
            edit_questions=False,
            questions=[Question({})],
            description=TemplateField(
                "description for {% if lot == 'digital-specialists' %}specialists{% else %}outcomes{% endif %}"
            )
        )

        assert section.filter(
            {"lot": lot},
            inplace_allowed=filter_inplace_allowed,
        ).description == expected_description

    @pytest.mark.parametrize("filter_inplace_allowed", (False, True,))
    @pytest.mark.parametrize("get_data_arg,expected_retval", (
        (MultiDict([('q1', 'false')]), {'q1': False},),
        (MultiDict([('q1', 'true')]), {'q1': True, 'q2': None},),
        (MultiDict([('q1', 'false'), ('q2', 'true')]), {'q1': False, 'q2': True},),
        (MultiDict([('q1', 'true'), ('q2', 'true')]), {'q1': True, 'q2': None},),
    ))
    def test_question_followup_get_data(self, filter_inplace_allowed, get_data_arg, expected_retval):
        section = ContentSection(
            slug='section',
            name=TemplateField('Section one'),
            prefill=False,
            editable=False,
            edit_questions=False,
            questions=[Question({'id': 'q1', 'followup': {'q2': [False]}, 'type': 'boolean'}),
                       Question({'id': 'q2', 'type': 'boolean'})]
        ).filter({}, inplace_allowed=filter_inplace_allowed)

        assert section.get_data(get_data_arg) == expected_retval
