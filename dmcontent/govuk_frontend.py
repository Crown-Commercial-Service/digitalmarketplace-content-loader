"""
Create forms to answer questions using govuk-frontend macros.


This module aims to solve the developer need of

    Given a content loader Question
    I want to create a form element using the GOV.UK Design System
    So that the user gets a good experience

in a way that requires the developer to know as little as possible about the
Question object in question.

The main function in this module is `render_question()`. It will take a content
loader Question and turn it into HTML that can be used directly in a template.

`render_question()` needs to be called from within a Jinja2 template, so it
should be added to your template environment. You can add it to all your
templates by adding it to your environment globals like so:

    >>> import jinja2
    >>> from dmcontent.govuk_frontend import render_question
    >>> env = jinja2.Environment()
    >>> env.globals["render_question"] = render_question

You will also need to make sure all the GOV.UK (and Digital Marketplace) macros
are in the template environment where you call `render_question()`; currently
this function can call (this is not an exhaustive list):

    - govukCharacterCount
    - govukCheckboxes
    - govukDateInput
    - govukFieldset
    - govukInput
    - govukLabel
    - govukRadios
    - dmListInput

`render_question()` should cover all the usual cases of creating a form from a
Question, but if for some reason you need to do more you can use
`from_question()` and `render()` individually; `render_question()` just calls
`render()` on the output of `from_question()`.

Read the docstring for `from_question()` for more detail on how Questions are
handled.
"""

from typing import List, Optional, Set, TYPE_CHECKING

import jinja2
from jinja2 import Markup, escape

from dmutils.forms.errors import govuk_error
from dmutils.forms.helpers import govuk_options

if TYPE_CHECKING:
    from dmcontent.questions import Question


__all__ = ["render_question", "from_question", "govuk_input", "govuk_label"]

# Version of govuk-frontend templates expected. This is just the default,
# set this in your app to change the behaviour of this code.
govuk_frontend_version = (2, 13, 0)


def from_question(
    question: 'Question', data: Optional[dict] = None, errors: Optional[dict] = None, **kwargs
) -> Optional[dict]:
    """Create parameters object for govuk-frontend macros from a question

    `from_question()` takes a `Question` and returns a dict containing the name of
    the govuk-frontend macro to call and the parameters to call it with, as
    well as associated components such as labels or fieldsets.

        >>> from dmcontent import Question
        >>> from_question(Question({'id': 'q1', 'type': 'text', 'question': ...})
        {'label': {...}, 'macro_name': 'govukInput', 'params': {...}}

    Calling the macro(s) with the parameters is then done by `render()`, below.
    If `render()` and all the macros you need are in your template environment,
    then no extra Jinja magic is required.

    `from_question()` mainly just takes care of dispatching the `Question`
    object to the right function (defined below) for further processing; if you
    need to handle a new type of `Question` try and follow that pattern.

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
    elif question.type == "boolean":
        return {
            "fieldset": govuk_fieldset(question, **kwargs),
            "macro_name": "govukRadios",
            "params": govuk_radios(question, data, errors, **kwargs)
        }
    elif question.type == "textbox_large":
        return {
            "label": govuk_label(question, **kwargs),
            "macro_name": "govukCharacterCount",
            "params": govuk_character_count(question, data, errors, **kwargs)
        }
    elif question.type == "multiquestion":
        return dm_multiquestion(question, data, errors, **kwargs)
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

    if question.get("type") == "boolean":
        if params.get("classes"):
            params["classes"] += " govuk-radios--inline"
        else:
            params["classes"] = "govuk-radios--inline"
        options = [{"label": "Yes", "value": "True"}, {"label": "No", "value": "False"}]
        params["items"] = govuk_options(options, str(data.get(question.id)))
    else:
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


def dm_multiquestion(
    question: 'Question', data: Optional[dict] = None, errors: Optional[dict] = None, **kwargs
) -> list:
    to_render = []

    if question.get("question_advice"):
        to_render.append(_question_advice(question))

    # We need to be able to skip followup questions. Questions which have
    # followups always come before the followup, so we create a variable
    # outside of the loop scope which is used to flag when a subsequent
    # question should be skipped. Followups are referred to by id in the
    # question object, so our variable should be a set of ids.
    to_skip: Set[str] = set()

    for q in question.questions:
        if q.id in to_skip:
            continue

        to_render.append(
            from_question(q, data, errors, is_page_heading=False)
        )

        if q.get("followup"):
            # flag that the followup question(s) should be skipped later
            to_skip.update(q.followup.keys())

            # convert the values in values_followup to str
            # to match the form input item values
            followups = {str(v): qs for v, qs in q.values_followup.items()}
            items = to_render[-1]["params"]["items"]

            for item in items:
                if item["value"] in followups:
                    followup_q = question.get_question(followups[item["value"]][0])
                    item["conditional"] = {
                        "html": from_question(followup_q, data, errors, is_page_heading=False)
                    }

    return to_render


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

    if question_type in ("checkboxes", "list", "radios", "boolean"):
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


def _question_advice(
    question: 'Question', **kwargs
) -> Markup:
    """Render `question_advice` for `question`"""
    return (
        Markup('<span class="dm-question-advice">\n')
        + question.question_advice
        + Markup('\n</span>')
    )


# TODO: The code in `render()` is more complicated than it needs to be because
# we are trying to maintain backwards compatibility with the interface of
# `from_question()`. Once all apps are using `render_question()` instead of
# `from_question()` we can safely change the objects emitted by `from_question()`
# and experiment a bit more.

@jinja2.contextfunction
def render(ctx, obj, *, question=None) -> Markup:
    """Call Jinja2 macros using Python objects

    We want to be able to create HTML using govuk-frontend macros within Python
    (not Jinja) code. To do that we need a template environment, so we have
    come up with a method of creating deferred call objects and a new function
    `render()` that evaluates the deferred calls.

    `render()` still needs to be called from within a Jinja2 template, but it
    should be able to handle expressions of arbitrary complexity (i.e. you can
    have a macro call which calls other macros in its arguments).

    For convenience `render()` will also accept strings (either `str` or
    `Markup`) and pass them through, and if given a list of objects it will
    call itself on each object and join the result into one piece of HTML.

    `render()` always returns `Markup` (i.e. unescaped HTML), so it should be
    used with caution. Do not use it on user input!!

    :type obj: list[dict or str or Markup] or dict or str or Markup
    """
    if isinstance(obj, list):
        return Markup("".join(render(ctx, el) for el in obj))
    elif isinstance(obj, dict):
        html = Markup("")
        if "label" in obj:
            html += ctx.resolve("govukLabel")(obj["label"])
        if "macro_name" in obj:
            macro = ctx.resolve(obj["macro_name"])
            params = obj.get("params", {}).copy()
            inner_html = Markup("")

            # TODO: this shouldn't be here
            if (
                "question_advice" not in params
                and question and question.get("question_advice")
            ):
                inner_html += question.question_advice + "\n"

            if params:
                # look for structures that are {'html': {'macro_name': ...}}
                # and render them
                def visit(inner_obj):
                    if isinstance(inner_obj, dict):
                        for k, v in inner_obj.items():
                            if (
                                k == "html"
                                and isinstance(v, dict)
                                and "macro_name" in v
                            ):
                                inner_obj["html"] = render(ctx, v)
                            else:
                                visit(v)
                    elif isinstance(inner_obj, list):
                        for el in inner_obj:
                            visit(el)

                visit(params)

                inner_html += Markup(macro(params))
            else:
                inner_html += Markup(macro())

            if "fieldset" in obj:
                inner_html = Markup(
                    ctx.resolve("govukFieldset")(obj["fieldset"], caller=lambda: inner_html)
                )

            html += inner_html

        return html
    elif isinstance(obj, (str, Markup)):
        return escape(obj)
    else:
        raise TypeError("render() expects a dict or string type, or a list of dicts or string types")


@jinja2.contextfunction
def render_question(
    ctx,
    question: 'Question',
    data: Optional[dict] = None,
    errors: Optional[dict] = None,
    **kwargs
) -> Markup:
    """Turn a content loader Question into HTML

    Convenience function that calls `render()` on the output of
    `from_question()`. In most circumstances this should be all you need.
    """
    to_render = from_question(question, data, errors, **kwargs)
    if to_render is None:
        raise jinja2.UndefinedError(f"unable to render question of type '{question.type}'")
    return render(
        ctx,
        to_render,
        question=question
    )
