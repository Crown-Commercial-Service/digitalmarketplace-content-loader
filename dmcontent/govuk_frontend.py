"""
Create forms to answer questions using govuk-frontend macros.
"""

from typing import Optional

from jinja2 import Markup, escape

from dmutils.forms.errors import govuk_error

from dmcontent.questions import Question


__all__ = ["govuk_input"]


def govuk_input(
    question: Question, data: Optional[dict] = None, errors: Optional[dict] = None
) -> dict:
    """Create govukInput macro parameters from a text question"""

    params = _params(question, data, errors)
    params["classes"] = "app-text-input--height-compatible"

    return params


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
        - label
        - name
        - value (optional)

    :returns: A dictionary with parameters that are generally useful for
              govuk-frontend component macros
    """
    params = {
        "id": f"input-{question.id}",
        "name": question.id,
    }

    label_text = question.question
    if question.is_optional:
        # GOV.UK Design System says
        # > mark the labels of optional fields with '(optional)'
        label_text += " (optional)"

    params["label"] = {
        # Style the label as a page heading, following the
        # GOV.UK Design System question pages pattern at
        # https://design-system.service.gov.uk/patterns/question-pages/
        "classes": "govuk-label--l",
        "isPageHeading": True,

        "text": label_text,
    }

    hint_html = Markup()
    if question.get("question_advice"):
        # Put the question advice inside the hint, wrapped in a div
        # We add the class .app-hint--text so the question advice
        # can be styled like a normal paragraph with the following Sass
        #
        #     .app-hint--text {
        #       @extend %govuk-body--m
        #     }
        hint_html += Markup('<div class="app-hint--text">\n')
        hint_html += escape(question.question_advice)
        hint_html += Markup("\n</div>")
        if question.get("hint"):
            hint_html += "\n"

    if question.get("hint"):
        hint_html += escape(question.hint)

    if hint_html:
        params["hint"] = {"html": hint_html}

    if data and question.id in data:
        params["value"] = data[question.id]

    if errors and question.id in errors:
        params["errorMessage"] = govuk_error(errors[question.id])["errorMessage"]

    return params
