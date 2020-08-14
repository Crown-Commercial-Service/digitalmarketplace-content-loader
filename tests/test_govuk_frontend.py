import pytest

from dmcontent.questions import Question

from dmcontent.govuk_frontend import (
    from_question, govuk_input, dm_list_input, govuk_fieldset, govuk_label, _params
)


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

    def test_from_question(self, question, snapshot):
        form = from_question(question)

        assert form["macro_name"] == "govukInput"
        assert form["params"] == snapshot

    def test_with_data(self, question, snapshot):
        data = {
            "title": "Find an individual specialist",
        }

        assert from_question(question, data) == snapshot

    def test_with_errors(self, question, snapshot):
        errors = {
            "title": {
                "input_name": "title",
                "href": "#input-title",
                "question": "What you want to call your requirements",
                "message": "Enter a title.",
            }
        }

        assert from_question(question, errors=errors) == snapshot


class TestDmListInput:
    @pytest.fixture
    def question(self):
        return Question(
            {
                "id": "culturalFitCriteria",
                "name": "Title",
                "question": "Cultural fit criteria",
                "question_advice": (
                    '<p class="govuk-body">Cultural fit is about how well you and the specialist work together</p>'
                ),
                "hint": "Enter at least one criteria",
                "number_of_items": 5,
                "type": "list",
            }
        )

    def test_dm_list_input(self, question, snapshot):
        assert dm_list_input(question) == snapshot

    def test_from_question(self, question, snapshot):
        form = from_question(question)

        assert form["macro_name"] == "dmListInput"
        assert form["params"] == snapshot

    def test_with_data(self, question, snapshot):
        data = {
            "culturalFitCriteria": ["Must know how to make tea", "Must believe unicorns"],
        }

        assert from_question(question, data) == snapshot

    def test_with_errors(self, question, snapshot):
        errors = {
            "culturalFitCriteria": {
                "input_name": "culturalFitCriteria",
                "href": "#input-culturalFitCriteria",
                "question": "Cultural fit criteria",
                "message": "Enter at least one criterion.",
            }
        }

        assert from_question(question, errors=errors) == snapshot


class TestGovukLabel:
    @pytest.fixture
    def question(self):
        return Question({"id": "question", "question": "Yes or no?"})

    def test_govuk_label(self, question):
        assert govuk_label(question) == {
            "classes": "govuk-label--l",
            "isPageHeading": True,
            "for": "input-question",
            "text": "Yes or no?",
        }

    def test_optional_question_has_optional_in_label_text(self, question):
        question.optional = True

        assert govuk_label(question)["text"] == "Yes or no? (optional)"

    def test_not_optional_question_does_not_have_optional_in_label_text(self, question):
        question.optional = False

        assert govuk_label(question)["text"] == "Yes or no?"


class TestGovukFieldset:
    @pytest.fixture
    def question(self):
        return Question({"id": "question", "question": "Enter your criteria"})

    def test_govuk_fieldset(self, question):
        assert govuk_fieldset(question) == {
            "legend": {
                "text": "Enter your criteria",
                "isPageHeading": True,
                "classes": "govuk-fieldset__legend--l"
            }
        }

    def test_optional_question_has_optional_in_legend_text(self, question):
        question.type = "list"
        question.optional = True

        assert govuk_fieldset(question)["legend"]["text"] == "Enter your criteria (optional)"

    def test_not_optional_question_does_not_have_optional_in_legend_text(self, question):
        question.type = "list"
        question.optional = False

        assert govuk_fieldset(question)["legend"]["text"] == "Enter your criteria"


class TestParams:
    @pytest.fixture
    def question(self):
        return Question({"id": "question", "question": "Yes or no?"})

    def test__params(self, question):
        assert _params(question) == {
            "id": "input-question",
            "name": "question",
        }

    def test_hint(self, question):
        question.hint = "Answer yes or no"

        assert _params(question)["hint"] == {
            "text": "Answer yes or no",
        }

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
