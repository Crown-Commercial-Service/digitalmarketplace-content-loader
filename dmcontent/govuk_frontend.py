"""
Create forms to answer questions using govuk-frontend macros.

The main function in this module is `from_question`. It should be possible to
do everything you might want to do just by calling `from_question` with a
content loader Question.

Read the docstring for `from_question` for more detail on how this works.
"""

from typing import List, Optional, TYPE_CHECKING

from dmutils.forms.errors import govuk_error
from dmutils.forms.helpers import govuk_options

if TYPE_CHECKING:
    from dmcontent.questions import Question


__all__ = ["from_question", "govuk_input", "govuk_label"]

# Version of govuk-frontend templates expected. This is just the default,
# set this in your app to change the behaviour of this code.
govuk_frontend_version = (2, 13, 0)


def from_question(
    question: 'Question', data: Optional[dict] = None, errors: Optional[dict] = None, **kwargs
) -> Optional[dict]:
    """Create parameters object for govuk-frontend macros from a question

    `from_question` aims to solve the developer need of

        Given a content loader Question
        I want to create a form element using the GOV.UK Design System
        So that the user gets a good experience

    in a way that requires the developer to know as little as possible about
    the Question object in question.

    `from_question` takes a Question and returns a dict containing the name of
    the govuk-frontend macro to call and the parameters to call it with, as
    well as associated components such as labels or fieldsets.  Calling the
    macro(s) with the parameters is left to the app developer.

        >>> from dmcontent import Question
        >>> from_question(Question({'id': 'q1', 'type': 'text', 'question': ...})
        {'label': {...}, 'macro_name': 'govukInput', 'params': {...}}

    A little bit of Jinja magic is required for this;  you need a table of
    macro names to macros in a Jinja template:

        {% set govuk_forms = {
            'govukInput': govukInput,
            'govukRadios': govukRadios,
            ...
        } %}

        {% set form = from_question(question) %}

        {% if form.label %}
        {{ govukLabel[form.label] }}
        {% endif %}
        {{ govuk_forms[form.macro_name](form.parameters) }}

    :param question: A Question or QuestionSummary
    :param data: A dict that may contain the answer for question
    :param errors: A dict which may contain an error message for the question

    :returns: A dict with the macro name, macro parameters, and labels, or None
              if we don't know how to handle this type of question
    """
    if question.type == "text" or question.type == "number":
        return {
            "label": govuk_label(question, **kwargs),
            "macro_name": "govukInput",
            "params": govuk_input(question, data, errors, **kwargs),
        }
    elif question.type == "pricing":
        return dm_pricing_input(question, data, errors, **kwargs)
    elif question.type == "date":
        return {
            "fieldset": govuk_fieldset(question, **kwargs),
            "macro_name": "govukDateInput",
            "params": govuk_date_input(question, data, errors, **kwargs),
        }
    elif question.type == "list":
        return {
            "macro_name": "dmListInput",
            "params": dm_list_input(question, data, errors, **kwargs)
        }
    elif question.type == "radios":
        return {
            "fieldset": govuk_fieldset(question, **kwargs),
            "macro_name": "govukRadios",
            "params": govuk_radios(question, data, errors, **kwargs)
        }
    elif question.type == "checkboxes":
        return {
            "fieldset": govuk_fieldset(question, **kwargs),
            "macro_name": "govukCheckboxes",
            "params": govuk_checkboxes(question, data, errors, **kwargs)
        }
    elif question.type == "textbox_large":
        return {
            "label": govuk_label(question, **kwargs),
            "macro_name": "govukCharacterCount",
            "params": govuk_character_count(question, data, errors, **kwargs)
        }
    else:
        return None


def govuk_input(
    question: 'Question', data: Optional[dict] = None, errors: Optional[dict] = None, **kwargs
) -> dict:
    """Create govukInput macro parameters from a text, number or pricing question"""

    kwargs.setdefault("classes", ["app-text-input--height-compatible"])
    params = _params(question, data, errors, **kwargs)

    if question.type in ("number", "pricing"):
        params["classes"] += " govuk-input--width-5"
        params["spellcheck"] = False
        if question.get("limits") and question.limits.get("integer_only") is True:
            params["inputmode"] = "numeric"
            params["pattern"] = "[0-9]*"

        if question.get("unit"):
            prefix_or_suffix = {"before": "prefix", "after": "suffix"}[question.unit_position]
            params[prefix_or_suffix] = {"text": question.unit}

        if kwargs.get("prefix_text"):
            params["prefix"] = {"text": kwargs["prefix_text"]}
        if kwargs.get("suffix_text"):
            params["suffix"] = {"text": kwargs["suffix_text"]}

        if params.get("pattern"):
            if params.get("prefix"):
                unit_regex = f"{params['prefix']['text']}?"
                params["pattern"] = unit_regex + params["pattern"]
            if params.get("suffix"):
                unit_regex = f"{params['suffix']['text']}?"
                params["pattern"] += unit_regex

    return params


def govuk_checkboxes(
    question: 'Question', data: Optional[dict] = None, errors: Optional[dict] = None, **kwargs
) -> dict:
    """Create govukCheckboxes macro parameters from a checkboxes question"""

    return govuk_radios(question, data, errors, **kwargs)


def govuk_date_input(
    question: 'Question', data: Optional[dict] = None, errors: Optional[dict] = None, **kwargs
) -> dict:
    """Create govukDateInput macro parameters from a date question"""

    params = _params(question, data, errors)

    params["namePrefix"] = question.id

    params["items"] = [
        {
            "name": "day",
            "classes": "app-text-input--height-compatible govuk-input--width-2"
        },
        {
            "name": "month",
            "classes": "app-text-input--height-compatible govuk-input--width-2"
        },
        {
            "name": "year",
            "classes": "app-text-input--height-compatible govuk-input--width-4"
        }
    ]

    for item in params["items"]:
        if data:
            answer_key = f"{question.id}-{item['name']}"
            if data.get(answer_key):
                item["value"] = data[answer_key]
        if errors and errors.get(question.id):
            item["classes"] += ' govuk-input--error'

    return params


def govuk_radios(
    question: 'Question', data: Optional[dict] = None, errors: Optional[dict] = None, **kwargs
) -> dict:
    """Create govukRadios macro parameters from a radios question"""

    if data is None:
        data = {}

    # we don't pass data to _params because govukRadios deals with value differently
    params = _params(question, errors=errors)

    # govukRadios wants idPrefix, not id
    del params["id"]
    params["idPrefix"] = f"input-{question.id}"

    params["items"] = govuk_options(question.options, data.get(question.id))

    return params


def dm_list_input(
    question: 'Question', data: Optional[dict] = None, errors: Optional[dict] = None, **kwargs
) -> dict:
    """Create dmListInput macro parameters from a list question"""

    params = _params(question, data, errors)

    # Params that are not common to other components
    params["addButtonName"] = "item"
    params["maxItems"] = question.number_of_items
    params["items"] = []
    params["itemLabelPrefix"] = str(question.question)

    params["fieldset"] = govuk_fieldset(question, **kwargs)

    if question.question_advice:
        params["question_advice"] = question.question_advice

    if data and question.id in data:
        for item in data[question.id]:
            params["items"].append(
                {
                    "value": item
                }
            )

    return params


def dm_pricing_input(
    question: 'Question', data: Optional[dict] = None, errors: Optional[dict] = None, **kwargs
) -> dict:
    """Create several parameters for several components based on fields in pricing question"""

    if data is None:
        data = {}

    # There can either be multiple fields from the set {"maximum_price",
    # "minimum_price", "pricing_unit", "pricing_interval"}, or a single field
    # "price". If there is just a price field we don't want a fieldset.
    if len(question.fields) == 1:
        return {
            "label": govuk_label(question, **kwargs),
            "macro_name": "govukInput",
            "params": govuk_input(
                question,
                data,
                errors,
                input_id=question.fields["price"],
                prefix_text="£",
            ),
        }

    # TODO: Handle pricing questions with multiple fields. For now (for the
    # briefs frontend) we only need to handle the simple case. Have a look at
    # branch ldeb-spike-pricing-input-multiple-fields for a sketch of how to do
    # the multiple field case.
    raise NotImplementedError("cannot yet handle pricing question with multiple fields")


def govuk_label(question: 'Question', *, is_page_heading: bool = True, **kwargs) -> dict:
    """
    :param bool is_page_heading: If True, the label will be set to display as a page heading
    """
    input_id: str = kwargs.get("input_id", question.id)
    label_classes: List[str] = kwargs.get("label_classes", [])

    label = {
        "for": f"input-{input_id}",
        "text": get_label_text(question, **kwargs),
    }
    if is_page_heading:
        label_classes += ["govuk-label--l"]
        label["isPageHeading"] = is_page_heading

    if label_classes:
        label["classes"] = " ".join(label_classes)

    return label


def govuk_fieldset(question: 'Question', *, is_page_heading: bool = True, **kwargs) -> dict:
    """
    :param bool is_page_heading: If True, the legend will be set to display as a page heading
    """

    fieldset = {
        "legend": {
            "classes": "govuk-fieldset__legend--m",
            "text": get_label_text(question),
        }
    }

    if is_page_heading:
        fieldset["legend"]["isPageHeading"] = is_page_heading
        fieldset["legend"]["classes"] = "govuk-fieldset__legend--l"

    return fieldset


def govuk_character_count(
    question: 'Question', data: Optional[dict] = None, errors: Optional[dict] = None, **kwargs
) -> dict:
    params = _params(question, data, errors)

    params["spellcheck"] = True

    if question.get("max_length_in_words"):
        params["maxwords"] = question.max_length_in_words

    return params


def get_href(question: 'Question', **kwargs) -> str:
    """The default url fragment for a question's input field."""
    # This code unfortunately couples us to the template used to render the question
    # TODO: be better
    href = f"#input-{question.id}"

    question_type = question.get("type")

    if question_type == "checkbox_tree":
        href = f"{href}-1-1"

    if question_type == "date":
        href = f"{href}-day"

    # govuk-frontend version 3 and up doesn't have suffixes for the first
    # input of a fieldset by default, so we can skip this logic
    if govuk_frontend_version[0] >= 3:
        return href

    if question_type in ("checkboxes", "list", "radios"):
        href = f"{href}-1"

    return href


def get_label_text(question: 'Question', **kwargs) -> str:
    label_text = kwargs.get("label_text", question.question)
    if question.is_optional:
        # GOV.UK Design System says
        # > mark the labels of optional fields with '(optional)'
        label_text += " (optional)"

    return label_text


def _params(
    question: 'Question', data: Optional[dict] = None, errors: Optional[dict] = None, **kwargs
) -> dict:
    """Common parameters for govuk-frontent components

    The GOV.UK Design System macro library govuk-frontend has a consistent set
    of parameters that are used across almost all of its component macros.

    This function abstracts out those common parameters to hopefully simplify
    creating parameter sets for specific macros.

    *This function should however be considered an implementation detail of
    this module, and you should avoid using it outside of this file (hence the
    underscore).*

    The parameters handled by this function include:

        - errorMessage (optional)
        - hint (optional)
        - id
        - name
        - value (optional)

    :returns: A dictionary with parameters that are generally useful for
              govuk-frontend component macros
    """
    classes: Optional[List[str]] = kwargs.get("classes")
    hint_text: Optional[str] = kwargs.get("hint_text", question.get("hint"))
    input_id: str = kwargs.get("input_id", question.id)

    params = {
        "id": f"input-{input_id}",
        "name": input_id,
    }

    if classes:
        params["classes"] = " ".join(classes)

    if hint_text:
        params["hint"] = {"text": hint_text}
        if kwargs.get("hint_classes"):
            params["hint"]["classes"] = " ".join(kwargs["hint_classes"])

    if data and data.get(input_id):
        params["value"] = data[input_id]

    if errors and errors.get(input_id):
        params["errorMessage"] = govuk_error(errors[input_id])["errorMessage"]

    return params
