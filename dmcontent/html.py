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

from dmutils.filters import capitalize_first, format_links, replace_newlines_with_breaks


def to_html(
    question_summary, *, capitalize_first: bool = False, format_links: bool = False
) -> Markup:
    """Format the value of a QuestionSummary as HTML.

    :param bool capitalize_first: If True, the first letter of any text will be capitalized
    :param bool format_links: If True any HTTP URLs in any text will be turned into HTML <a> elements
    """
    kwargs = {
        "capitalize_first": capitalize_first,
        "format_links": format_links,
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
    elif question_type == "list":
        return list_to_html(question_value, **kwargs)
    elif question_type == "checkboxes":
        return list_to_html(question_value)
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


def to_summary_list_rows(questions) -> List[dict]:
    """Convert a collection of QuestionSummarys into rows for govukSummaryList.

    This method expects that each question in `questions` is a
    QuestionSummary i.e. each question includes service data.
    """
    return [
        {"key": {"text": question.label}, "value": {"html": to_html(question)}}
        for question in questions
        if not question.is_empty
    ]


def text_to_html(value, **kwargs):
    if "capitalize_first" in kwargs:
        value = capitalize_first(value)

    if "format_links" in kwargs:
        value = format_links(value)

    if "preserve_line_breaks" in kwargs:
        # replace_newlines_with_breaks escapes its input anyway
        # so wrapping with Markup here is fine.
        value = Markup(replace_newlines_with_breaks(value))

    return escape(value)


def list_to_html(value, **kwargs):
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
