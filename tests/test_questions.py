# coding=utf-8

from dmcontent.content_loader import ContentQuestion


class TestBaseQuestion(object):
    def test_form_fields_property(self):
        question = ContentQuestion({
            "id": "example",
            "type": "text"
        })
        assert question.form_fields == ['example']


class TestPricing(object):
    def test_form_fields(self):
        question = ContentQuestion({
            "id": "example",
            "type": "pricing",
            "fields": {
                "minimum_price": "priceMin",
                "maximum_price": "priceMax",
            }
        })
        assert sorted(question.form_fields) == sorted(['priceMin', 'priceMax'])

    def test_required_form_fields_property(self):
        question = ContentQuestion({
            "id": "example",
            "type": "pricing",
            "fields": {
                "minimum_price": "priceMin",
                "maximum_price": "priceMax",
            }
        })
        assert sorted(question.required_form_fields) == sorted(['priceMin', 'priceMax'])

    def test_required_form_fields_property_when_optional(self):
        question = ContentQuestion({
            "id": "example",
            "type": "pricing",
            "optional": True,
            "fields": {
                "minimum_price": "priceMin",
                "maximum_price": "priceMax",
            }
        })
        assert question.required_form_fields == []

    def test_required_form_fields_property_with_optional_fields(self):
        question = ContentQuestion({
            "id": "example",
            "type": "pricing",
            "fields": {
                "minimum_price": "priceMin",
                "maximum_price": "priceMax",
            },
            "optional_fields": [
                "minimum_price"
            ]
        })
        assert question.required_form_fields == ['priceMax']


class TestMultiquestion(object):
    def test_form_fields(self):
        question = ContentQuestion({
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
        })
        assert question.form_fields == ['example2', 'example3']

    def test_required_form_fields(self):
        question = ContentQuestion({
            "id": "example",
            "type": "multiquestion",
            "questions": [
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
            ]
        })
        assert question.required_form_fields == ['example2']
