import pytest

from unittest import mock

import jinja2
from jinja2 import Markup

from dmcontent.questions import Pricing, Question

from dmcontent.govuk_frontend import (
    from_question,
    govuk_character_count,
    govuk_date_input,
    govuk_input,
    govuk_checkboxes,
    govuk_radios,
    dm_list_input,
    dm_pricing_input,
    govuk_fieldset,
    govuk_label,
    _params,
    render,
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

    def test_govuk_input_classes(self, question, snapshot):
        assert govuk_input(question)["classes"] == "app-text-input--height-compatible"
        assert govuk_input(question, classes=["app-input"])["classes"] == "app-input"

    def test_from_question(self, question, snapshot):
        form = from_question(question)

        assert form["macro_name"] == "govukInput"
        assert form["params"] == snapshot

    def test_from_question_with_is_page_heading_false(self, question, snapshot):
        form = from_question(question, is_page_heading=False)

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


class TestNumberInput:
    @pytest.fixture
    def question(self):
        return Question({
            "id": "howMany",
            "question": "How many?",
            "type": "number",
        })

    def test_govuk_input(self, question, snapshot):
        assert govuk_input(question) == snapshot

    def test_govuk_input_asking_for_whole_numbers(self, question):
        """Test that we follow Design System guidance on asking for numbers

        https://design-system.service.gov.uk/components/text-input/#numbers
        """

        question.limits = {"integer_only": True}

        params = govuk_input(question)

        assert params["inputmode"] == "numeric"
        assert params["pattern"] == "[0-9]*"
        assert params["spellcheck"] is False

    @pytest.mark.parametrize("integer_only", (False, None))
    def test_govuk_input_asking_for_decimal_numbers(self, integer_only, question):
        """Test that we follow Design System guidance on asking for numbers

        https://design-system.service.gov.uk/components/text-input/#numbers
        """

        if integer_only is False:
            question.limits = {"integer_only": False}

        params = govuk_input(question)

        assert "inputmode" not in params
        assert params["spellcheck"] is False

    def test_govuk_input_prefix(self, question):
        question.unit = "£"
        question.unit_position = "before"

        params = govuk_input(question)

        assert params["prefix"] == {"text": "£"}

    def test_govuk_input_prefix_text_kwarg(self, question):
        params = govuk_input(question, prefix_text="£")

        assert params["prefix"] == {"text": "£"}

    def test_govuk_input_suffix(self, question):
        question.unit = "%"
        question.unit_position = "after"

        params = govuk_input(question)

        assert params["suffix"] == {"text": "%"}

    def test_govuk_input_suffix_text_kwarg(self, question):
        params = govuk_input(question, suffix_text="%")

        assert params["suffix"] == {"text": "%"}

    @pytest.mark.parametrize(
        "unit, unit_position, expected_pattern",
        (
            ("%", "after", "[0-9]*%?"),
            ("£", "before", "£?[0-9]*"),
        ),
    )
    def test_govuk_input_pattern_includes_prefix_or_suffix(
        self,
        unit,
        unit_position,
        expected_pattern,
        question,
    ):
        question.limits = {"integer_only": True}

        question.unit = unit
        question.unit_position = unit_position

        params = govuk_input(question)

        assert params["pattern"] == expected_pattern

    def test_govuk_input_width(self, question):
        """Number inputs should be a reasonably small width"""
        params = govuk_input(question)
        assert "govuk-input--width-5" in params["classes"]

    def test_from_question(self, question, snapshot):
        form = from_question(question)

        assert "label" in form
        assert form["macro_name"] == "govukInput"
        assert form["params"] == snapshot

    def test_from_question_with_data(self, question, snapshot):
        data = {"howMany": "10"}

        form = from_question(question, data)

        assert form["params"]["value"] == "10"
        assert form == snapshot

    def test_from_question_with_errors(self, question, snapshot):
        errors = {
            "howMany": {
                "input_name": "howMany",
                "href": "#input-howMany",
                "question": "How many?",
                "message": "Enter how many",
            }
        }

        form = from_question(question, errors=errors)

        assert "errorMessage" in form["params"]
        assert form == snapshot


class TestRadios:
    @pytest.fixture
    def question(self):
        return Question(
            {
                "id": "yesOrNo",
                "name": "Yes or no",
                "question": "Yes or no?",
                "type": "radios",
                "options": [
                    {"label": "Yes", "value": "yes"},
                    {"label": "No", "value": "no"},
                ],
            }
        )

    def test_govuk_radios(self, question, snapshot):
        assert govuk_radios(question) == snapshot

    def test_govuk_radios_id_prefix(self, question):
        params = govuk_radios(question)

        assert "id" not in params
        assert params["idPrefix"] == "input-yesOrNo"

    def test_govuk_radios_options_with_descriptions(self, question):
        question.options = [
            {"label": "Yes", "value": "yes", "description": "Affirmative."},
            {"label": "No", "value": "no", "description": "Negative."},
        ]

        assert govuk_radios(question)["items"] == [
            {"text": "Yes", "value": "yes", "hint": {"text": "Affirmative."}},
            {"text": "No", "value": "no", "hint": {"text": "Negative."}},
        ]

    def test_from_question(self, question, snapshot):
        form = from_question(question)

        assert "fieldset" in form
        assert form["macro_name"] == "govukRadios"
        assert form["params"] == snapshot

    def test_from_question_with_is_page_heading_false(self, question, snapshot):
        fieldset = from_question(question)["fieldset"]

        assert "isPageHeading" not in fieldset or fieldset["isPageHeading"] is False
        assert fieldset == snapshot

    def test_from_question_with_data(self, question, snapshot):
        data = {"yesOrNo": "yes"}

        form = from_question(question, data)

        assert "value" not in form["params"]
        assert form["params"]["items"][0]["checked"] is True
        assert "checked" not in form["params"]["items"][1]
        assert form == snapshot

    def test_from_question_with_errors(self, question, snapshot):
        errors = {
            "yesOrNo": {
                "input_name": "title",
                "href": "#input-yesOrNo",
                "question": "Yes or no?",
                "message": "Select yes or no,",
            }
        }

        form = from_question(question, errors=errors)

        assert "errorMessage" in form["params"]
        assert form == snapshot


class TestBoolean:
    @pytest.fixture
    def question(self):
        return Question(
            {
                "id": "yesOrNo",
                "name": "Yes or no",
                "question": "Yes or no?",
                "type": "boolean"
            }
        )

    def test_govuk_radios_with_type_boolean(self, question, snapshot):
        params = govuk_radios(question)

        assert "id" not in params
        assert params["idPrefix"] == "input-yesOrNo"
        assert params["classes"] == "govuk-radios--inline"

    def test_boolean_options_are_yes_and_no(self, question):
        assert govuk_radios(question)["items"] == [
            {"value": "True", "text": "Yes"},
            {"value": "False", "text": "No"},
        ]


class TestCheckboxes:
    @pytest.fixture
    def question(self):
        return Question(
            {
                "id": "oneAndAnother",
                "name": "One and another",
                "question": "Choose one and/or another",
                "type": "checkboxes",
                "options": [
                    {"label": "One", "value": "one"},
                    {"label": "Another", "value": "another"},
                ],
            }
        )

    def test_govuk_checkboxes(self, question, snapshot):
        assert govuk_checkboxes(question) == snapshot

    def test_govuk_checkboxes_id_prefix(self, question):
        params = govuk_checkboxes(question)

        assert "id" not in params
        assert params["idPrefix"] == "input-oneAndAnother"

    def test_govuk_checkbox_options_with_descriptions(self, question):
        question.options = [
            {"label": "One", "value": "one", "description": "This is the first thing."},
            {"label": "Another", "value": "another", "description": "This is another thing."},
        ]

        assert govuk_checkboxes(question)["items"] == [
            {"text": "One", "value": "one", "hint": {"text": "This is the first thing."}},
            {"text": "Another", "value": "another", "hint": {"text": "This is another thing."}},
        ]

    def test_from_question(self, question, snapshot):
        form = from_question(question)

        assert "fieldset" in form
        assert form["macro_name"] == "govukCheckboxes"
        assert form["params"] == snapshot

    def test_from_question_with_is_page_heading_false(self, question, snapshot):
        fieldset = from_question(question)["fieldset"]

        assert "isPageHeading" not in fieldset or fieldset["isPageHeading"] is False
        assert fieldset == snapshot

    def test_from_question_with_data(self, question, snapshot):
        data = {"oneAndAnother": "one"}

        form = from_question(question, data)

        assert "value" not in form["params"]
        assert form["params"]["items"][0]["checked"] is True

        data = {"oneAndAnother": ["one", "another"]}
        form = from_question(question, data)
        assert form["params"]["items"][0]["checked"] is True
        assert form["params"]["items"][1]["checked"] is True
        assert form == snapshot

    def test_from_question_with_errors(self, question, snapshot):
        errors = {
            "oneAndAnother": {
                "input_name": "title",
                "href": "#input-oneAndAnother",
                "question": "Select one and/or another.",
                "message": "Select one or another",
            }
        }

        form = from_question(question, errors=errors)

        assert "errorMessage" in form["params"]
        assert form == snapshot


class TestDateInput:
    @pytest.fixture
    def question(self):
        return Question(
            {
                "id": "startDate",
                "name": "Latest start date",
                "question": "What is the latest start date?",
                "type": "date"
            }
        )

    def test_govuk_date_input(self, question, snapshot):
        assert govuk_date_input(question) == snapshot

    def test_govuk_date_input_name_prefix(self, question):
        params = govuk_date_input(question)

        assert params["namePrefix"] == question.id

    def test_govuk_date_input_classes(self, question):
        params = govuk_date_input(question)

        for item in params["items"]:
            assert "app-text-input--height-compatible" in item["classes"]

    def test_from_question(self, question, snapshot):
        form = from_question(question)

        assert "fieldset" in form
        assert form["macro_name"] == "govukDateInput"
        assert form["params"] == snapshot

    def test_from_question_with_is_page_heading_false(self, question, snapshot):
        fieldset = from_question(question)["fieldset"]

        assert "isPageHeading" not in fieldset or fieldset["isPageHeading"] is False
        assert fieldset == snapshot

    def test_from_question_with_data(self, question, snapshot):
        data = {"startDate-day": 1, "startDate-month": 12, "startDate-year": 2020}

        form = from_question(question, data)

        assert "value" not in form["params"]
        assert form["params"]["items"][0]["value"] == 1
        assert form["params"]["items"][1]["value"] == 12
        assert form["params"]["items"][2]["value"] == 2020
        assert form == snapshot

    def test_from_question_with_errors(self, question, snapshot):
        errors = {
            "startDate": {
                "input_name": "startDate",
                "href": "#input-startDate-day",
                "question": "What is the latest start date?",
                "message": "Enter a start date",
            }
        }

        form = from_question(question, errors=errors)

        assert "errorMessage" in form["params"]
        assert form == snapshot


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

    def test_from_question_with_is_page_heading_false(self, question, snapshot):
        form = from_question(question, is_page_heading=False)

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


class TestDmPricingInput:
    @staticmethod
    def assert_params(test, form):
        """Apply a test to all params dictionaries in form"""
        __tracebackhide__ = True
        if "params" in form:
            return test(form["params"])
        elif "components" in form:
            for component in form["components"]:
                assert test(component["params"])
        else:
            raise ValueError("form should have params or components with params")

    @pytest.fixture
    def price_question(self):
        return Pricing({
            "id": "cost",
            "question": "What's the cost?",
            "type": "pricing",
            "fields": {
                "price": "cost",
            },
        })

    @pytest.fixture
    def pricing_question(self):
        return Pricing({
            "id": "priceRange",
            "question": "What's the price range?",
            "type": "pricing",
            "fields": {
                "minimum_price": "minPrice",
                "maximum_price": "maxPrice",
            },
        })

    @pytest.fixture(params=["price_question"])
    def question(self, request):
        return request.getfixturevalue(request.param)

    def test_dm_pricing_input_with_price_field(self, price_question, snapshot):
        form = dm_pricing_input(price_question)

        assert "components" not in form
        assert form["macro_name"]
        assert form["label"]
        assert form["params"]["id"] == "input-cost"
        assert form == snapshot

    def test_dm_pricing_input_with_multiple_fields(self, pricing_question, snapshot):
        with pytest.raises(NotImplementedError):
            dm_pricing_input(pricing_question)

    def test_dm_pricing_input_is_page_heading_false(self, question):
        form = dm_pricing_input(question, is_page_heading=False)

        if "label" in form:
            assert "isPageHeading" not in form["label"]
        elif "fieldset" in form:
            assert "isPageHeading" not in form["fieldset"]
        else:
            raise ValueError("form should have label or fieldset")

    def test_dm_pricing_input_prefix_and_suffix(self, question):
        form = dm_pricing_input(question)

        self.assert_params(
            lambda params: params["prefix"]["text"] == "£",
            form
        )

    def test_from_question(self, question, snapshot):
        assert from_question(question) == snapshot

    def test_from_question_with_data(self, question, snapshot):
        data = {
            "cost": "1.00",
            "minPrice": "10.00",
            "maxPrice": "50.00",
        }

        form = from_question(question, data)

        self.assert_params(
            lambda params: params["value"] in data.values(),
            form
        )

        assert form == snapshot

    def test_from_question_with_errors(self, question, snapshot):
        errors = {
            "cost": {
                "input_name": "cost",
                "href": "#input-cost",
                "question": "What's the cost?",
                "message": "Enter a cost.",
            },
            "priceRange": {
                "input_name": "priceRange",
                "href": "#input-priceRange-minPrice",
                "question": "What's the price range?",
                "message": "Enter a price range.",
            },
        }

        form = from_question(question, errors=errors)

        if "params" in form:
            assert form["params"]["errorMessage"]
        elif "components" in form:
            pytest.skip("TODO: get errors working with pricing form with multiple fields")
            assert form["errorMessage"]
            # TODO: get errors working for indivual fields in the pricing form
            # this will require changes to validation of pricing forms
            for component in form["components"]:
                assert "--error" in component["params"]["classes"]
        else:
            raise ValueError("form should have params or a fieldset")

        assert form == snapshot


class TestGovukCharacterCount:
    @pytest.fixture
    def question(self):
        return Question(
            {
                "id": "description",
                "name": "Description",
                "question": "Describe the specialist's role",
                "question_advice": "Describe the team the specialist will be working with on this project.",
                "type": "textbox_large",
                "hint": "Enter at least one word, and no more than 100",
                "max_length_in_words": 100
            }
        )

    @pytest.fixture
    def question_without_word_count(self):
        return Question(
            {
                "id": "description",
                "name": "Description",
                "question": "Describe the specialist's role",
                "question_advice": "Describe the team the specialist will be working with on this project.",
                "type": "textbox_large"
            }
        )

    def test_govuk_character_count(self, question, snapshot):
        assert govuk_character_count(question) == snapshot

    def test_govuk_character_count_spellcheck_is_true(self, question):
        params = govuk_character_count(question)

        assert params["spellcheck"] is True

    def test_from_question(self, question, snapshot):
        form = from_question(question)

        assert form["macro_name"] == "govukCharacterCount"
        assert form["params"] == snapshot

    def test_question_with_no_max_word_length_does_not_have_maxwords_in_params(self, question_without_word_count):
        assert "maxwords" not in govuk_character_count(question_without_word_count)

    def test_with_data(self, question, snapshot):
        data = {
            "description": "The specialist must know how to make tea and work well with unicorns.",
        }

        assert from_question(question, data) == snapshot

    def test_with_errors(self, question, snapshot):
        errors = {
            "description": {
                "input_name": "description",
                "href": "#input-description",
                "question": "Description",
                "message": "Enter a description of the specialist's role.",
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

    def test_input_id_kwarg(self, question):
        assert govuk_label(question, input_id="q1")["for"] == "input-q1"

    def test_label_classes_kwarg(self, question):
        assert "app-label" in govuk_label(question, label_classes=["app-label"])["classes"]

    def test_label_text_kwarg(self, question):
        assert govuk_label(question, label_text="This is a label")["text"] == "This is a label"

    def test_is_page_heading_false_removes_classes_and_ispageheading(self, question):
        assert govuk_label(question, is_page_heading=False) == {
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

    def test_is_page_heading_false_removes_classes_and_ispageheading(self, question):
        assert govuk_fieldset(question, is_page_heading=False) == {
            "legend": {
                "classes": "govuk-fieldset__legend--m",
                "text": "Enter your criteria"
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

    def test_classes_kwarg(self, question):
        assert _params(question, classes=["app-input"])["classes"] == "app-input"
        assert _params(question, classes=["app-input", "app-input--l"])["classes"] == "app-input app-input--l"

    def test_input_id_kwarg(self, question):
        params = _params(question, input_id="question")
        assert params["id"] == "input-question"
        assert params["name"] == "question"

    def test_hint(self, question):
        question.hint = "Answer yes or no"

        assert _params(question)["hint"] == {
            "text": "Answer yes or no",
        }

    def test_hint_classes_kwarg(self, question):
        question.hint = "Choose yes or no"

        assert _params(question, hint_classes=["app-hint"])["hint"]["classes"] == "app-hint"

    def test_value_is_present_if_question_answer_is_in_data(self, question):
        data = {"question": "Yes"}

        assert _params(question, data)["value"] == "Yes"

    def test_value_is_not_present_if_question_answer_is_not_in_data(self, question):
        data = {"another_question": "Maybe"}

        assert "value" not in _params(question, data)

    def test_value_is_not_present_if_question_answer_is_none(self, question):
        data = {"another_question": None}

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

    def test_error_message_is_not_present_if_question_error_is_none(self, question):
        errors = {"another_question": None}

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


class TestRender:
    @pytest.fixture
    def context(self):
        return mock.Mock()

    @pytest.fixture
    def env(self):
        env = jinja2.Environment(lstrip_blocks=True, trim_blocks=True)
        env.globals["render"] = render
        return env

    def test_it_returns_markup(self, context):
        assert isinstance(render(context, []), Markup)
        assert isinstance(render(context, ""), Markup)
        assert isinstance(render(context, "Hello World"), Markup)
        assert isinstance(render(context, Markup("<p>Hello World</p>")), Markup)

    def test_it_returns_the_empty_string_if_called_with_nothing(self, context):
        assert render(context, []) == ""
        assert render(context, "") == ""

    def test_it_escapes_strings(self, context):
        assert render(context, "<p>Hello World</p>") == "&lt;p&gt;Hello World&lt;/p&gt;"

    def test_it_does_not_escape_markup(self, context):
        assert render(context, Markup("<p>Hello World</p>")) == "<p>Hello World</p>"

    def test_it_joins_lists_of_strings(self, context):
        assert render(context, [Markup("<p>"), "Hello World", Markup("</p>")]) \
            == Markup("<p>Hello World</p>")

    def test_it_is_passed_context_automatically_when_called_in_jinja_template(self, env):
        assert env.from_string(
            "{{ render([]) }}"
        ).render() == ""

    def test_it_calls_jinja_macros(self, env):
        template = env.from_string("""{% macro test() -%}
foo
{%- endmacro %}
{{ render([{'macro_name': 'test'}]) }}""")
        assert template.render() == "foo"

    def test_it_calls_macros_with_params(self, env):
        test_macro = mock.Mock(return_value="bar")
        template = env.from_string(
            "{{ render([{'macro_name': 'test', 'params': {'a': 1, 'b': 2}}]) }}"
        )
        assert template.render(test=test_macro) == "bar"
        assert test_macro.called_with({"a": 1, "b": 2})

    def test_jinja_macros_are_not_escaped(self, env):
        template = env.from_string("""{% macro test() -%}
<p>foo</p>
{%- endmacro %}
{{ render([{'macro_name': 'test'}]) }}""")
        assert template.render() == "<p>foo</p>"

        template = env.from_string("""{% macro test(params) -%}
<p>foo</p>
{%- endmacro %}
{{ render([{'macro_name': 'test', 'params': {'bar': 'baz'}}]) }}""")
        assert template.render() == "<p>foo</p>"

    def test_it_can_wrap_jinja_macros_in_fieldset(self, env):
        template = env.from_string("""{% macro test() -%}
bar
{%- endmacro %}
{% macro govukFieldset(params) -%}
<fieldset>{{ caller() }}</fieldset>
{%- endmacro %}
{{ render([{'macro_name': 'test', 'fieldset': None}]) }}""")

        assert template.render() == "<fieldset>bar</fieldset>"

    def test_it_calls_fieldset_with_params(self, env):
        test_macro = mock.Mock(return_value="foo")
        test_govuk_fieldset = mock.Mock(
            side_effect=lambda params, caller: params["fizz"]
        )
        template = env.from_string(
            "{{ render([{'macro_name': 'test', 'fieldset': {'fizz': 'buzz'}}]) }}"
        )
        assert template.render(test=test_macro, govukFieldset=test_govuk_fieldset) \
            == "buzz"
        assert test_govuk_fieldset.call_args_list == [
            mock.call({"fizz": "buzz"}, caller=mock.ANY)
        ]

    def test_macro_call_params_can_contain_macro_calls_in_html_key(self, env):
        template = env.from_string("""{% macro test() -%}
<p>foo</p>
{%- endmacro %}
{% macro wrapper(params) -%}
<div>{{ params.html | safe }}</div>
{%- endmacro %}
{{ render([{'macro_name': 'wrapper', 'params': {'html': {'macro_name': 'test'}}}]) }}""")
        assert template.render() == "<div><p>foo</p></div>"

    def test_macro_call_params_can_contain_macro_calls_in_html_key_even_if_nested(self, env):
        template = env.from_string("""{% macro test() -%}
<p>foo</p>
{%- endmacro %}
{% macro wrapper(params) -%}
{% for item in params['items'] -%}
{% if item.conditional -%}
<div>{{ item.conditional.html | safe }}</div>
{%- endif %}
{%- endfor %}
{%- endmacro %}
{{ render([{
    'macro_name': 'wrapper',
    'params': {'items': [{'conditional': {'html': {'macro_name': 'test'}}}]},
}]) }}""")
        assert template.render() == "<div><p>foo</p></div>"
