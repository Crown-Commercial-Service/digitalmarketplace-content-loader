"""
Create forms to answer questions using govuk-frontend macros.

The main function in this module is `from_question`. It should be possible to
do everything you might want to do just by calling `from_question` with a
content loader Question.

Read the docstring for `from_question` for more detail on how this works.
"""

from typing import Optional

from dmutils.forms.errors import govuk_error
from dmutils.forms.helpers import govuk_options

from dmcontent.questions import Question


__all__ = ["from_question", "govuk_input", "govuk_label"]


def from_question(
    question: Question, data: Optional[dict] = None, errors: Optional[dict] = None, **kwargs
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
    if question.type == "text":
        return {
            "label": govuk_label(question, **kwargs),
            "macro_name": "govukInput",
            "params": govuk_input(question, data, errors, **kwargs),
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
    question: Question, data: Optional[dict] = None, errors: Optional[dict] = None, **kwargs
) -> dict:
    """Create govukInput macro parameters from a text question"""

    params = _params(question, data, errors)
    params["classes"] = "app-text-input--height-compatible"

    return params


def govuk_checkboxes(
    question: Question, data: Optional[dict] = None, errors: Optional[dict] = None, **kwargs
) -> dict:
    """Create govukCheckboxes macro parameters from a checkboxes question"""

    return govuk_radios(question, data, errors, **kwargs)


def govuk_radios(
    question: Question, data: Optional[dict] = None, errors: Optional[dict] = None, **kwargs
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
    question: Question, data: Optional[dict] = None, errors: Optional[dict] = None, **kwargs
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


def govuk_label(question: Question, *, is_page_heading: bool = True, **kwargs) -> dict:
    """
    :param bool is_page_heading: If True, the label will be set to display as a page heading
    """

    label = {
        "for": f"input-{question.id}",
        "text": get_label_text(question),
    }
    if is_page_heading:
        label["classes"] = "govuk-label--l"
        label["isPageHeading"] = is_page_heading

    return label


def govuk_fieldset(question: Question, *, is_page_heading: bool = True, **kwargs) -> dict:
    """
    :param bool is_page_heading: If True, the legend will be set to display as a page heading
    """

    fieldset = {
        "legend": {
            "text": get_label_text(question),
        }
    }

    if is_page_heading:
        fieldset["legend"]["isPageHeading"] = is_page_heading
        fieldset["legend"]["classes"] = "govuk-fieldset__legend--l"

    return fieldset


def govuk_character_count(
    question: Question, data: Optional[dict] = None, errors: Optional[dict] = None, **kwargs
) -> dict:
    params = _params(question, data, errors)

    if question.get("max_length_in_words"):
        params["maxwords"] = question.max_length_in_words

    return params


def get_label_text(question: Question) -> str:
    label_text = question.question
    if question.is_optional:
        # GOV.UK Design System says
        # > mark the labels of optional fields with '(optional)'
        label_text += " (optional)"

    return label_text


def _params(
    question: Question, data: Optional[dict] = None, errors: Optional[dict] = None
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
    params = {
        "id": f"input-{question.id}",
        "name": question.id,
    }

    if question.get("hint"):
        params["hint"] = {"text": question.hint}

    if data and data.get(question.id):
        params["value"] = data[question.id]

    if errors and errors.get(question.id):
        params["errorMessage"] = govuk_error(errors[question.id])["errorMessage"]

    return params
