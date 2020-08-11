import pytest

from jinja2 import Markup

from dmcontent.questions import Question

from dmcontent.govuk_frontend import govuk_input, _params


class TestTextInput:
    @pytest.fixture
    def question(self):
        return Question(
            {
                "id": "title",
                "name": "Title",
                "question": "What you want to call your requirements",
                "question_advice": "This will help you to refer to your requirements",
                "hint": "100 characters maximum",
                "type": "text",
            }
        )

    def test_govuk_input(self, question, snapshot):
        assert govuk_input(question) == snapshot

    def test_with_data(self, question, snapshot):
        data = {
            "title": "Find an individual specialist",
        }

        assert govuk_input(question, data) == snapshot

    def test_with_errors(self, question, snapshot):
        errors = {
            "title": {
                "input_name": "title",
                "href": "#input-title",
                "question": "What you want to call your requirements",
                "message": "Enter a title.",
            }
        }

        assert govuk_input(question, errors=errors) == snapshot


class TestParams:
    @pytest.fixture
    def question(self):
        return Question({"id": "question", "question": "Yes or no?"})

    def test_govuk_input(self, question):
        assert _params(question) == {
            "id": "input-question",
            "name": "question",
            "label": {
                "classes": "govuk-label--l",
                "isPageHeading": True,
                "text": "Yes or no?",
            },
        }

    def test_hint(self, question):
        question.hint = "Answer yes or no"

        assert _params(question)["hint"] == {
            "html": "Answer yes or no",
        }

    def test_hint_is_escaped(self, question):
        question.hint = "<script>"

        assert _params(question)["hint"]["html"] == "&lt;script&gt;"

    def test_question_advice_is_part_of_hint(self, question):
        question.question_advice = "You should answer yes or no."

        hint = _params(question)["hint"]

        assert hint == {
            "html": '<div class="app-hint--text">\n'
            "You should answer yes or no.\n"
            "</div>"
        }
        assert isinstance(hint["html"], Markup)

    def test_question_advice_is_escaped(self, question):
        question.question_advice = "<script>"

        assert _params(question)["hint"] == {
            "html": '<div class="app-hint--text">\n' "&lt;script&gt;\n" "</div>"
        }

    def test_question_advice_and_hint(self, question):
        question.hint = "Answer yes or no"
        question.question_advice = "You should answer yes or no."

        assert _params(question)["hint"] == {
            "html": '<div class="app-hint--text">\n'
            "You should answer yes or no.\n"
            "</div>\n"
            "Answer yes or no"
        }

    def test_optional_question_has_optional_in_label_text(self, question):
        question.optional = True

        assert _params(question)["label"]["text"] == "Yes or no? (optional)"

    def test_not_optional_question_does_not_have_optional_in_label_text(self, question):
        question.optional = False

        assert _params(question)["label"]["text"] == "Yes or no?"

    def test_value_is_present_if_question_answer_is_in_data(self, question):
        data = {"question": "Yes"}

        assert _params(question, data)["value"] == "Yes"

    def test_value_is_not_present_if_question_answer_is_not_in_data(self, question):
        data = {"another_question": "Maybe"}

        assert "value" not in _params(question, data)

    def test_error_message_is_present_if_question_error_is_in_errors(self, question):
        errors = {
            "question": {
                "input_name": "question",
                "href": "#input-question",
                "question": "Yes or no?",
                "message": "Answer yes or no.",
            }
        }

        assert _params(question, errors=errors)["errorMessage"] == {
            "text": "Answer yes or no."
        }

    def test_error_message_is_not_present_if_question_error_is_not_in_errors(
        self, question
    ):
        errors = {
            "another_question": {
                "input_name": "another-question",
                "href": "#input-another-question",
                "question": "Are you sure?",
                "message": "Enter whether you are sure or not.",
            }
        }

        assert "errorMessage" not in _params(question, errors=errors)

    def test_value_and_error_message(self, question):
        data = {"question": "Definitely"}
        errors = {
            "question": {
                "input_name": "question",
                "href": "#input-question",
                "question": "Yes or no?",
                "message": "Answer yes or no only.",
            }
        }

        params = _params(question, data, errors)
        assert params["value"] == "Definitely"
        assert params["errorMessage"]["text"] == "Answer yes or no only."
