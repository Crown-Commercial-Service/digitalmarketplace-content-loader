# coding=utf-8

import pytest

from werkzeug.datastructures import OrderedMultiDict
from dmcontent.content_loader import ContentQuestion
from dmcontent.utils import TemplateField
from dmcontent import ContentTemplateError


class QuestionTest(object):
    def test_get_question(self):
        question = self.question()
        assert question.get_question('example') == question

    def test_get_question_unknown_id(self):
        question = self.question()
        assert question.get_question('other') is None

    def test_get_data_unknown_key(self):
        assert self.question().get_data({'other': 'other value'}) == {}

    def test_required_form_fields_optional_question(self):
        assert self.question(optional=True).required_form_fields == []

    def test_get_question_ids_by_unknown_type(self):
        assert self.question().get_question_ids(type='other') == []

    def test_label_name(self):
        assert self.question(name='name').label == 'name'

    def test_label_question(self):
        assert self.question(question='question').label == 'question'

    def test_label_name_and_question(self):
        assert self.question(name='name', question='question').label == 'name'

    def test_question_repr(self):
        assert 'data=' in repr(self.question())

    def test_question_filter_without_dependencies(self):
        question = self.question()
        assert question.filter({}) is not None
        assert question.filter({}) is not question

    def test_question_filter_with_dependencies_that_match(self):
        question = self.question(depends=[{"on": "lot", "being": ["lot-1"]}])
        assert question.filter({"lot": "lot-1"}) is not None
        assert question.filter({"lot": "lot-1"}) is not question

    def test_question_filter_with_dependencies_that_are_not_matched(self):
        question = self.question(depends=[{"on": "lot", "being": ["lot-1"]}])
        assert question.filter({"lot": "lot-2"}) is None

    def test_question_without_template_tags_are_unchanged(self):
        question = self.question(
            name=TemplateField("Name"),
            question=TemplateField("Question"),
            hint=TemplateField("Hint"),
            question_advice=TemplateField("Advice")
        ).filter({})

        assert question.name == "Name"
        assert question.question == "Question"
        assert question.hint == "Hint"
        assert question.question_advice == "Advice"

    def test_question_fields_are_templated(self):
        question = self.question(
            name=TemplateField("Name {{ name }}"),
            question=TemplateField("Question {{ question }}"),
            hint=TemplateField("Hint {{ hint }}"),
            question_advice=TemplateField("Advice {{ advice }}")
        ).filter({
            "name": "zero",
            "question": "one",
            "hint": "two",
            "advice": "three"
        })

        assert question.name == "Name zero"
        assert question.question == "Question one"
        assert question.hint == "Hint two"
        assert question.question_advice == "Advice three"

    def test_question_fields_are_templated_on_access_if_filter_wasnt_called(self):
        question = self.question(
            name=TemplateField("Name {{ name }}"),
            question=TemplateField("Question"),
        )

        with pytest.raises(ContentTemplateError):
            question.name

        assert question.question == "Question"


class TestText(QuestionTest):
    def question(self, **kwargs):
        data = {
            "id": "example",
            "type": "text"
        }
        data.update(kwargs)

        return ContentQuestion(data)

    def test_get_data(self):
        assert self.question().get_data({'example': 'value'}) == {'example': 'value'}

    def test_get_data_with_assurance(self):
        assert self.question(assuranceApproach='2answers-type1').get_data(
            {'example': 'value1', 'example--assurance': 'assurance value'}
        ) == {'example': {'value': 'value1', 'assurance': 'assurance value'}}

    def test_get_data_with_assurance_unknown_key(self):
        assert self.question(assuranceApproach='2answers-type1').get_data({'other': 'value'}) == {'example': {}}

    def test_get_data_with_assurance_only(self):
        assert self.question(assuranceApproach='2answers-type1').get_data(
            {'example--assurance': 'assurance value'}
        ) == {'example': {'assurance': 'assurance value'}}

    def test_form_fields(self):
        assert self.question().form_fields == ['example']

    def test_required_form_fields(self):
        assert self.question().required_form_fields == ['example']

    def test_get_question_ids(self):
        assert self.question().get_question_ids() == ['example']

    def test_get_question_ids_by_type(self):
        assert self.question().get_question_ids(type='text') == ['example']


class TestPricing(QuestionTest):
    def question(self, **kwargs):
        data = {
            "id": "example",
            "type": "pricing",
            "fields": {
                "minimum_price": "priceMin",
                "maximum_price": "priceMax",
            }
        }
        data.update(kwargs)

        return ContentQuestion(data)

    def test_get_data(self):
        assert self.question().get_data(
            {'priceMin': '10', 'priceMax': '20'}
        ) == {'priceMin': '10', 'priceMax': '20'}

    def test_get_data_partial(self):
        assert self.question().get_data(
            {'priceMax': '20'}
        ) == {'priceMax': '20'}

    def test_form_fields(self):
        assert sorted(self.question().form_fields) == sorted(['priceMin', 'priceMax'])

    def test_required_form_fields(self):
        assert sorted(self.question().required_form_fields) == sorted(['priceMin', 'priceMax'])

    def test_required_form_fields_optional_fields(self):
        question = self.question(optional_fields=["minimum_price"])
        assert question.required_form_fields == ['priceMax']

    def test_get_question_ids(self):
        assert self.question().get_question_ids() == ['example']

    def test_get_question_ids_by_type(self):
        assert self.question().get_question_ids(type='pricing') == ['example']


class TestMultiquestion(QuestionTest):
    def question(self, **kwargs):
        data = {
            "id": "example",
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
        data.update(kwargs)

        return ContentQuestion(data)

    def test_get_question_nested(self):
        question = self.question()
        assert question.get_question('example3') == question.questions[1]

    def test_get_data(self):
        assert self.question().get_data(
            {'example2': 'value2', 'example3': 'value3'}
        ) == {'example2': 'value2', 'example3': 'value3'}

    def test_get_data_ignores_own_key(self):
        assert self.question().get_data(
            {'example': 'value', 'example3': 'value3'}
        ) == {'example3': 'value3'}

    def test_form_fields(self):
        assert self.question().form_fields == ['example2', 'example3']

    def test_form_fields_optional_question(self):
        assert self.question(optional=True).form_fields == ['example2', 'example3']

    def test_required_form_fields(self):
        assert self.question().required_form_fields == ['example2', 'example3']

    def test_required_form_fields_optional_nested_question(self):
        question = self.question(questions=[
            {
                "id": "example2",
                "type": "text",
                "optional": False,
            },
            {
                "id": "example3",
                "type": "text",
                "optional": True,
            }
        ])
        assert question.required_form_fields == ['example2']

    def test_get_question_ids(self):
        assert self.question().get_question_ids() == ['example2', 'example3']

    def test_get_question_ids_by_type(self):
        assert self.question().get_question_ids(type='number') == ['example3']

    def test_nested_question_fields_are_templated(self):
        question = self.question(
            questions=[{
                "id": "example2",
                "type": "text",
                "question": TemplateField("Question {{ name }}")
            }]
        ).filter({
            "name": "one",
        })

        assert question.get_question('example2').question == "Question one"



class TestCheckboxes(QuestionTest):
    def question(self, **kwargs):
        data = {
            "id": "example",
            "type": "checkboxes",
            "options": [
                {"label": "Wrong label", "value": "value"},
                {"label": "Option label", "value": "value1"},
                {"label": "Wrong label", "value": "value2"},
            ]
        }
        data.update(kwargs)

        return ContentQuestion(data)

    def test_get_data(self):
        assert self.question().get_data(
            OrderedMultiDict([('example', 'value1'), ('example', 'value2')])
        ) == {'example': ['value1', 'value2']}

    def test_get_data_unknown_key(self):
        assert self.question().get_data({'other': 'other value'}) == {'example': None}

    def test_get_data_with_assurance(self):
        assert self.question(assuranceApproach='2answers-type1').get_data(
            OrderedMultiDict([('example', 'value1'), ('example', 'value2'), ('example--assurance', 'assurance value')])
        ) == {'example': {'value': ['value1', 'value2'], 'assurance': 'assurance value'}}

    def test_get_data_with_assurance_unknown_key(self):
        assert self.question(assuranceApproach='2answers-type1').get_data({'other': 'value'}) == {'example': {}}

    def test_get_data_with_assurance_only(self):
        assert self.question(assuranceApproach='2answers-type1').get_data(
            {'example--assurance': 'assurance value'}
        ) == {'example': {'assurance': 'assurance value'}}


class QuestionSummaryTest(object):
    def test_value_missing(self):
        question = self.question().summary({})
        assert question.value == ''

    def test_answer_required_value_missing(self):
        question = self.question().summary({})
        assert question.answer_required

    def test_answer_required_optional_question(self):
        question = self.question(optional=True).summary({})
        assert not question.answer_required

    def test_is_empty_value_missing(self):
        question = self.question().summary({})
        assert question.is_empty

    def test_is_empty_optional_question(self):
        question = self.question(optional=True).summary({})
        assert question.is_empty


class TestTextSummary(QuestionSummaryTest):
    def question(self, **kwargs):
        data = {
            "id": "example",
            "type": "text"
        }
        data.update(kwargs)

        return ContentQuestion(data)

    def test_value(self):
        question = self.question().summary({'example': 'textvalue'})
        assert question.value == 'textvalue'

    def test_value_empty(self):
        question = self.question().summary({'example': ''})
        assert question.value == ''

    def test_answer_required(self):
        question = self.question().summary({'example': 'value1'})
        assert not question.answer_required

    def test_is_empty(self):
        question = self.question().summary({'example': 'value1'})
        assert not question.is_empty


class TestRadiosSummary(TestTextSummary):
    def question(self, **kwargs):
        data = {
            "id": "example",
            "type": "radios",
            "options": [
                {"label": "Wrong label", "value": "value"},
                {"label": "Option label", "value": "value1"},
                {"label": "Other label", "value": "value2"},
            ]
        }
        data.update(kwargs)

        return ContentQuestion(data)

    def test_value_returns_matching_option_label(self):
        question = self.question().summary({'example': 'value1'})
        assert question.value == 'Option label'


class TestCheckboxesSummary(QuestionSummaryTest):
    def question(self, **kwargs):
        data = {
            "id": "example",
            "type": "checkboxes",
            "options": [
                {"label": "Wrong label", "value": "value"},
                {"label": "Option label", "value": "value1"},
                {"label": "Other label", "value": "value2"},
            ]
        }
        data.update(kwargs)

        return ContentQuestion(data)

    def test_value(self):
        question = self.question().summary({'example': ['value1', 'value2']})
        assert question.value == ['value1', 'value2']

    def test_value_with_assurance(self):
        question = self.question(assuranceApproach='2answers-type1').summary(
            {'example': {'assurance': 'assurance value', 'value': ['value1', 'value2']}}
        )
        assert question.value == ['value1', 'value2']

    def test_value_with_before_summary_value(self):
        question = self.question(before_summary_value=['value0']).summary({'example': ['value1', 'value2']})
        assert question.value == ['value0', 'value1', 'value2']

    def test_value_with_before_summary_value_if_empty(self):
        question = self.question(before_summary_value=['value0']).summary({})
        assert question.value == ['value0']


class TestNumberSummary(QuestionSummaryTest):
    def question(self, **kwargs):
        data = {
            "id": "example",
            "type": "number",
        }
        data.update(kwargs)

        return ContentQuestion(data)

    def test_value(self):
        question = self.question().summary({'example': 23.41})
        assert question.value == 23.41

    def test_value_zero(self):
        question = self.question().summary({'example': 0})
        assert question.value == 0

    def test_value_without_unit(self):
        question = self.question().summary({'example': '12.20'})
        assert question.value == '12.20'

    def test_value_adds_unit_before(self):
        question = self.question(unit=u"£", unit_position="before").summary({'example': '12.20'})
        assert question.value == u'£12.20'

    def test_value_adds_unit_after(self):
        question = self.question(unit=u"£", unit_position="after").summary({'example': '12.20'})
        assert question.value == u'12.20£'

    def test_value_doesnt_add_unit_if_value_is_empty(self):
        question = self.question(unit=u"£", unit_position="after").summary({})
        assert question.value == u''

    def test_value_adds_unit_for_questions_with_assertion(self):
        question = self.question(unit=u"£", unit_position="after", assuranceApproach="2answers-type1").summary({
            'example': {'value': 15,  'assurance': 'Service provider assertion'}
        })
        assert question.value == u'15£'

    def test_answer_required(self):
        question = self.question().summary({'example': 0})
        assert not question.answer_required

    def test_is_empty(self):
        question = self.question().summary({'example': 0})
        assert not question.is_empty


class TestPricingSummary(QuestionSummaryTest):
    def question(self, **kwargs):
        data = {
            "id": "example",
            "type": "pricing",
            "fields": {
                "price": "price",
                "minimum_price": "priceMin",
                "maximum_price": "priceMax",
                "price_unit": "priceUnit",
                "price_interval": "priceInterval",
                "hours_for_price": "priceHours",
            }
        }
        data.update(kwargs)

        return ContentQuestion(data)

    def test_value(self):
        question = self.question().summary({'priceMin': '20.41', 'priceMax': '25.00'})
        assert question.value == u'£20.41 to £25.00'

    def test_value_without_price_min(self):
        question = self.question().summary({'priceMax': '25.00'})
        assert question.value == ''

    def test_value_price_field(self):
        question = self.question().summary({'price': '20.41'})
        assert question.value == u'£20.41'

    def test_value_without_price_max(self):
        question = self.question().summary({'priceMin': '20.41'})
        assert question.value == u'£20.41'

    def test_value_with_hours_for_price(self):
        question = self.question().summary({'priceMin': '20.41', 'priceHours': '8'})
        assert question.value == u'8 for £20.41'

    def test_value_with_unit(self):
        question = self.question().summary({'priceMin': '20.41', 'priceMax': '25.00', 'priceUnit': 'service'})
        assert question.value == u'£20.41 to £25.00 per service'

    def test_value_with_interval(self):
        question = self.question().summary({'priceMin': '20.41', 'priceMax': '25.00', 'priceInterval': 'day'})
        assert question.value == u'£20.41 to £25.00 per day'

    def test_value_with_unit_and_interval(self):
        question = self.question().summary(
            {'priceMin': '20.41', 'priceMax': '25.00', 'priceUnit': 'service', 'priceInterval': 'day'}
        )
        assert question.value == u'£20.41 to £25.00 per service per day'


class TestMultiquestionSummary(QuestionSummaryTest):
    def question(self, **kwargs):
        data = {
            "id": "example",
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
        data.update(kwargs)

        return ContentQuestion(data)

    def test_value(self):
        question = self.question().summary({'example2': 'value2', 'example3': 'value3'})
        assert question.value == question.questions

    def test_value_missing(self):
        question = self.question().summary({})
        assert question.value == []

    def test_answer_required(self):
        question = self.question().summary({'example2': 'value2', 'example3': 'value3'})
        assert not question.answer_required

    def test_is_empty(self):
        question = self.question().summary({'example': 'value2', 'example3': 'value3'})
        assert not question.is_empty

    def test_answer_required_partial(self):
        question = self.question().summary({'example3': 'value3'})
        assert question.answer_required

    def test_is_empty_partial(self):
        question = self.question().summary({'example2': 'value2'})
        assert not question.is_empty
