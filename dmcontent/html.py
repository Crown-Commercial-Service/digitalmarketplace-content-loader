"""
Code to format content summary values as HTML.

This module has two main functions:

    to_html(): Format the value of a QuestionSummary as HTML.
    to_summary_list_rows(): Turn a collection of QuestionSummarys into
                            rows for govukSummaryList.

The logic for how to format values is based on that in the deprecated
digitalmarketplace-frontend-toolkit, specifically the summary content macros in
`templates/summary-content.html`.

Note: this code doesn't provide for formatting of assurance approach
information, as that hasn't been used since G-Cloud 8.
"""

from typing import List

from jinja2 import Markup, escape

import dmutils.filters as filters


def to_html(
    question_summary,
    *,
    capitalize_first: bool = False,
    format_links: bool = False,
    open_links_in_new_tab: bool = False
) -> Markup:
    """Format the value of a QuestionSummary as HTML.

    :param bool capitalize_first: If True, the first letter of any text will be capitalized
    :param bool format_links: If True any HTTP URLs in any text will be turned into HTML <a> elements
    """
    kwargs = {
        "capitalize_first": capitalize_first,
        "format_links": format_links,
        "open_links_in_new_tab": open_links_in_new_tab,
    }

    # Duck type the value of question_summary
    question_type = None
    try:
        question_type = question_summary["type"]
    except TypeError:
        raise TypeError("to_html() expects a QuestionSummary")

    # filter_value falls back to value if the question doesn't have any
    # filter_label properties, so we can use filter_value safely in
    # all cases.
    question_value = question_summary.filter_value

    if question_type == "boolean":
        return boolean_to_html(question_value)
    elif question_type == "number":
        return number_to_html(question_value)
    elif question_type in ("list", "checkboxes"):
        return list_to_html(question_value, **kwargs)
    elif question_type == "boolean_list":
        return boolean_list_to_html(question_value)
    elif question_type == "multiquestion":
        return multiquestion_to_html(question_summary)
    elif question_type == "upload":
        return upload_to_html(question_summary)
    elif question_type == "textbox_large":
        return text_to_html(question_value, preserve_line_breaks=True, **kwargs)
    else:
        return text_to_html(question_value, **kwargs)


def to_summary_list_rows(questions, *, filter_empty=True, **kwargs) -> List[dict]:
    """Convert a collection of QuestionSummarys into rows for govukSummaryList.

    This method expects that each question in `questions` is a
    QuestionSummary i.e. each question includes service data.

    `kwargs` are passed to `to_html`.

    :param bool filter_empty: Whether or not to include unanswered questions in the rows
    """
    return [
        to_summary_list_row(question, **kwargs)
        for question in questions
        if not (question.is_empty and filter_empty)
    ]


def to_summary_list_row(question, *, action_link=None, **kwargs) -> List[dict]:
    """Convert a QuestionSummary into a row for govukSummaryList.

    This method expects a QuestionSummary.

    `kwargs` are passed to `to_html`.

    :param string action_link: A link for the row's action
    """
    if action_link is not None:
        empty_message = question.get("empty_message", "Not answered")
        question_label = question.label + ' (Optional)' if question.is_optional else question.label
        if question.is_empty:
            question_value = (
                Markup(f'<a class="govuk-link" href="{action_link}">{empty_message}</a>')
            )
        else:
            question_value = to_html(question, **kwargs)
        if not question.is_empty:
            output = {
                "key": {"text": question_label},
                "value": {"html": question_value},
                "actions": {
                    "items": [{
                        "href": action_link,
                        "text": "Edit",
                        "visuallyHiddenText": question.label
                    }]
                }
            }
        else:
            output = {
                "key": {"text": question_label},
                "value": {"html": question_value}
            }
    else:
        question_label = question.label
        question_value = to_html(question, **kwargs)
        output = {
            "key": {"text": question_label},
            "value": {"html": question_value}
        }

    return output


def text_to_html(
        value,
        *,
        capitalize_first=False,
        format_links=False,
        preserve_line_breaks=False,
        open_links_in_new_tab=False,
        **kwargs
):
    """Convert a string to a HTML string, optionally modifying it first.

    :param bool capitalize_first: If True, the first letter of any text will be capitalized
    :param bool format_links: If True any HTTP URLs in any text will be turned into HTML <a> elements
    :param bool preserve_line_breaks: If True HTTP newline sequences (\\r\\n) will be turned into HTML <br> elements
    :param bool open_links_in_new_tab: If True formatted HTTP URL <a> elements will open in a new tab
    """
    if capitalize_first is True:
        value = filters.capitalize_first(value)

    if format_links is True:
        value = filters.format_links(value, open_links_in_new_tab)

    if preserve_line_breaks is True:
        # replace_newlines_with_breaks escapes its input anyway
        # so wrapping with Markup here is fine.
        value = Markup(filters.replace_newlines_with_breaks(value))

    return escape(value)


def list_to_html(value, **kwargs):
    if len(value) == 0:
        return text_to_html("", **kwargs)
    if len(value) == 1:
        return text_to_html(value[0], **kwargs)

    lines = ['<ul class="govuk-list govuk-list--bullet">']
    for item in value:
        lines.append(f"  <li>{text_to_html(item, **kwargs)}</li>")
    lines.append("</ul>")
    html = "\n".join(lines)
    return Markup(html)


def boolean_to_html(value):
    if value is True:
        return text_to_html("Yes")
    if value is False:
        return text_to_html("No")


def boolean_list_to_html(value_list):
    html_values = []
    for value in value_list:
        html_values.append(boolean_to_html(value))
    return list_to_html(html_values)


def number_to_html(value):
    return text_to_html(str(value))


def upload_to_html(question):
    return Markup(f'<a class="govuk-link" href="{question.filter_value}">{question.label}</a>')


def multiquestion_to_html(summary):
    lines = []
    for index, question in enumerate(summary.questions):
        if not question.is_empty:
            if (index == 0):
                classes = "govuk-body govuk-!-margin-top-0 govuk-!-margin-bottom-1"
            else:
                classes = "govuk-body govuk-!-margin-top-3 govuk-!-margin-bottom-1"
            lines.append(f'<p class="{classes}">{escape(question.label)}</p>')
            lines.append(f'<div>{to_html(question)}</div>')
    html = "\n".join(lines)
    return Markup(html)
