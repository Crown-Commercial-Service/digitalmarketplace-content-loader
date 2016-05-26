# coding=utf-8

from dmcontent.content_loader import ContentQuestion


class TestText(object):
    def question(self, **kwargs):
        data = {
            "id": "example",
            "type": "text"
        }
        data.update(kwargs)

        return ContentQuestion(data)

    def test_form_fields_property(self):
        assert self.question().form_fields == ['example']


class TestPricing(object):
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

    def test_form_fields(self):
        assert sorted(self.question().form_fields) == sorted(['priceMin', 'priceMax'])

    def test_required_form_fields_property(self):
        assert sorted(self.question().required_form_fields) == sorted(['priceMin', 'priceMax'])

    def test_required_form_fields_property_when_optional(self):
        question = self.question(optional=True)
        assert question.required_form_fields == []

    def test_required_form_fields_property_with_optional_fields(self):
        question = self.question(optional_fields=["minimum_price"])
        assert question.required_form_fields == ['priceMax']


class TestMultiquestion(object):
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
                    "type": "text",
                }
            ]
        }
        data.update(kwargs)

        return ContentQuestion(data)

    def test_form_fields(self):
        assert self.question().form_fields == ['example2', 'example3']

    def test_required_form_fields(self):
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


class TestContentQuestionSummary(object):
    def test_question_value_with_no_options(self):
        question = ContentQuestion({
            "id": "example",
            "type": "text",
        }).summary({'example': 'value1'})

        assert question.value == 'value1'

    def test_question_value_returns_matching_option_label(self):
        question = ContentQuestion({
            "id": "example",
            "type": "checkboxes",
            "options": [
                {"label": "Wrong label", "value": "value"},
                {"label": "Option label", "value": "value1"},
                {"label": "Wrong label", "value": "value11"},
            ]
        }).summary({'example': 'value1'})

        assert question.value == 'Option label'

    def test_number_questions_without_unit(self):
        question = ContentQuestion({
            "id": "example",
            "type": "number",
        }).summary({'example': '12.20'})

        assert question.value == '12.20'

    def test_number_questions_adds_unit_before(self):
        question = ContentQuestion({
            "id": "example",
            "type": "number",
            "unit": u"£",
            "unit_position": "before",
        }).summary({'example': '12.20'})

        assert question.value == u'£12.20'

    def test_number_questions_adds_unit_after(self):
        question = ContentQuestion({
            "id": "example",
            "type": "number",
            "unit": u"£",
            "unit_position": "after",
        }).summary({'example': '12.20'})

        assert question.value == u'12.20£'

    def test_question_unit_not_added_if_value_is_empty(self):
        question = ContentQuestion({
            "id": "example",
            "type": "number",
            "unit": u"£",
            "unit_position": "after",
        }).summary({})

        assert question.value == u''

    def test_question_unit_added_for_questions_with_assertion(self):
        question = ContentQuestion({
            "id": "example",
            "type": "number",
            "unit": u"£",
            "unit_position": "after",
            'assuranceApproach': '2answers-type1',
        }).summary({'example': {'value': 15,  'assurance': 'Service provider assertion'}})

        assert question.value == u'15£'
