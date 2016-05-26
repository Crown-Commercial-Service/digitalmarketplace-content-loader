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
