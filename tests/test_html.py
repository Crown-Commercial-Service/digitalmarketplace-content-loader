from textwrap import dedent

import jinja2
import pytest
from jinja2 import Markup

from dmcontent.content_loader import ContentManifest
from dmcontent.html import text_to_html, to_html, to_summary_list_rows


@pytest.fixture
def content_summary():
    content = ContentManifest(
        [
            {
                "slug": "first_section",
                "name": "First Section",
                "questions": [
                    {
                        "id": "myBooleanTrue",
                        "type": "boolean",
                        "label": "Boolean question with answer True",
                    },
                    {
                        "id": "myBooleanFalse",
                        "type": "boolean",
                        "label": "Boolean question with answer False",
                    },
                    {
                        "id": "myBooleanList",
                        "type": "boolean_list",
                        "label": "Boolean list question",
                    },
                    {
                        "id": "myCheckbox",
                        "type": "checkboxes",
                        "label": "Checkboxes question",
                    },
                    {
                        "id": "myCheckboxWithOneItem",
                        "type": "checkboxes",
                        "label": "Checkboxes question with answer that checks only one item",
                    },
                    {"id": "myDate", "type": "date", "label": "Date question"},
                    {
                        "id": "myEmptyString",
                        "type": "text",
                        "question": "Text question with empty answer",
                    },
                    {
                        "id": "myFloat",
                        "type": "number",
                        "question": "Numeric question with decimal answer",
                    },
                    {
                        "id": "myInteger",
                        "type": "number",
                        "question": "Numeric question with integer answer",
                    },
                    {
                        "id": "myMultiquestion",
                        "type": "multiquestion",
                        "label": "Multiquestion",
                        "questions": [
                            {"id": "mq01", "type": "text", "label": "MQ One"},
                            {"id": "mq02", "type": "text", "question": "MQ Two"},
                        ],
                    },
                    {
                        "id": "myPricing",
                        "type": "pricing",
                        "label": "Pricing question",
                        "fields": {
                            "minimum_price": "pricing.min",
                            "maximum_price": "pricing.max",
                        },
                    },
                    {"id": "myRadio", "type": "radios", "label": "Radio button question"},
                    {"id": "mySimpleList", "type": "list", "label": "List question"},
                    {"id": "mySimpleText", "type": "text", "label": "Text question"},
                    {
                        "id": "myLinkText",
                        "type": "text",
                        "label": "Text question with a link in the answer",
                    },
                    {
                        "id": "myLinkTextarea",
                        "type": "textbox_large",
                        "label": "Text question with multiple lines and a link in the answer",
                    },
                    {
                        "id": "myLinkList",
                        "type": "list",
                        "label": "List question with links in the answer",
                    },
                    {
                        "id": "myLowercaseText",
                        "type": "text",
                        "label": "Text question with a lower-case answer",
                    },
                    {
                        "id": "myLowercaseTextarea",
                        "type": "textbox_large",
                        "question": "Text question with multiple lines and a lower-case answer",
                    },
                    {
                        "id": "myLowercaseList",
                        "type": "list",
                        "label": "List question with a lower-case answer",
                    },
                    {
                        "id": "myMultipleLines",
                        "type": "textbox_large",
                        "question": "Text question with multiple lines in the answer",
                    },
                    {"id": "myUpload", "type": "upload", "question": "Upload Question"},
                    {
                        "id": "myScriptInjection",
                        "type": "text",
                        "label": "Text question with HTML in the answer",
                    },
                    {
                        "id": "myUnansweredQuestion",
                        "type": "text",
                        "optional": True,
                        "label": "Optional question which is not answered",
                    },
                    {
                        "id": "myMultiquestionWithMultipleTypes",
                        "type": "multiquestion",
                        "label": "Multiquestion",
                        "questions": [
                            {"id": "mqText", "type": "text", "label": "Text question"},
                            {"id": "mqList", "type": "list", "question": "List question"},
                            {"id": "mqCheckbox", "type": "checkboxes", "question": "Checkbox question"},
                            {"id": "mqBoolean", "type": "boolean", "question": "Boolean question"},
                            {"id": "mqBooleanList", "type": "boolean_list", "question": "Boolean list question"},
                            {"id": "mqRadio", "type": "radios", "question": "Radios question"},
                            {"id": "mqUnanswered", "type": "text", "optional": True, "label": "Unanswered question"},
                            {"id": "mqUpload", "type": "upload", "question": "Upload question"}
                        ],
                    }
                ],
            }
        ]
    )
    return content.summary(
        {
            "myBooleanTrue": True,
            "myBooleanFalse": False,
            "myDate": "2016-02-18",
            "mySimpleText": "Hello World",
            "myInteger": 7,
            "myFloat": 23.45,
            "mySimpleList": ["Hello", "World"],
            "myRadio": "Selected radio value",
            "mq01": "Multiquestion answer 1",
            "mq02": "Multiquestion answer 2",
            "mqBoolean": True,
            "mqBooleanList": [True, False],
            "mqCheckbox": ["Check 1", "Check 2"],
            "mqList": ["Hello", "World"],
            "mqRadio": "Selected radio value",
            "mqText": "Multiquestion text answer",
            "mqUpload": "#",
            "myCheckbox": ["Check 1", "Check 2"],
            "myCheckboxWithOneItem": ["check 2"],
            "myBooleanList": [True, False, False, True],
            "myUpload": "#",
            "myLinkText": "https://www.gov.uk",
            "myLinkTextarea": "Here is a URL:\r\n\r\nhttps://www.gov.uk",
            "myLinkList": ["https://www.gov.uk", "https://www.gov.uk/"],
            "myLowercaseText": "text to be capitalised",
            "myLowercaseTextarea": "text to be capitalised\r\nwith a line break.",
            "myLowercaseList": ["line 1", "line 2"],
            "pricing.min": "20.41",
            "pricing.max": "25.00",
            "myMultipleLines": "Text with multiple lines.\r\n\r\nThis is the second line.",
            "myScriptInjection": "<script>do something bad</script>"
        }
    )


def test_text_to_html_takes_one_string_value_and_returns_markup():
    assert text_to_html("") == Markup("")
    assert text_to_html("Hello World") == Markup("Hello World")


def test_text_to_html_can_capitalize_first_letter():
    assert text_to_html("hello world", capitalize_first=True) == "Hello world"
    assert text_to_html("hello world", capitalize_first=False) == "hello world"
    assert text_to_html("hello world") == "hello world"


def test_text_to_html_can_format_links():
    assert text_to_html("https://gov.uk", format_links=True) == \
        Markup('<a href="https://gov.uk" class="app-break-link" rel="external">https://gov.uk</a>')
    assert text_to_html("https://gov.uk", format_links=False) == "https://gov.uk"
    assert text_to_html("https://gov.uk") == "https://gov.uk"


def test_text_to_html_can_preserve_line_breaks():
    assert text_to_html("First line.\r\nSecond line.", preserve_line_breaks=True) == \
        Markup("First line.<br>Second line.")
    assert text_to_html("First line.\r\nSecond line.", preserve_line_breaks=False) == \
        Markup("First line.\r\nSecond line.")
    assert text_to_html("First line.\r\nSecond line.") == \
        Markup("First line.\r\nSecond line.")


def test_to_html_raises_error_if_value_is_not_valid():
    with pytest.raises(TypeError):
        to_html(None)


def test_to_html_returns_value(content_summary):
    question = content_summary.get_question("myEmptyString")
    assert to_html(question) == ""


def test_to_html_returns_yes_if_boolean_true(content_summary):
    question = content_summary.get_question("myBooleanTrue")
    assert to_html(question) == "Yes"


def test_to_html_returns_no_if_boolean_false(content_summary):
    question = content_summary.get_question("myBooleanFalse")
    assert to_html(question) == "No"


def test_to_html_returns_text_as_html(content_summary):
    question = content_summary.get_question("mySimpleText")
    assert to_html(question) == "Hello World"


def test_to_html_returns_text_for_number(content_summary):
    integer_question = content_summary.get_question("myInteger")
    float_question = content_summary.get_question("myFloat")
    assert to_html(integer_question) == "7"
    assert to_html(float_question) == "23.45"


def test_to_html_returns_html_if_question_type_is_multiquestion(content_summary):
    question = content_summary.get_question("myMultiquestion")
    expected = dedent(
        """\
    <p class="govuk-body govuk-!-margin-top-0 govuk-!-margin-bottom-1">MQ One</p>
    <div>Multiquestion answer 1</div>
    <p class="govuk-body govuk-!-margin-top-3 govuk-!-margin-bottom-1">MQ Two</p>
    <div>Multiquestion answer 2</div>"""
    )
    assert to_html(question) == expected


def test_to_html_returns_html_with_multiquestion_sub_types(content_summary):
    question = content_summary.get_question("myMultiquestionWithMultipleTypes")
    expected = dedent(
        """\
    <p class="govuk-body govuk-!-margin-top-0 govuk-!-margin-bottom-1">Text question</p>
    <div>Multiquestion text answer</div>
    <p class="govuk-body govuk-!-margin-top-3 govuk-!-margin-bottom-1">List question</p>
    <div><ul class="govuk-list govuk-list--bullet">
      <li>Hello</li>
      <li>World</li>
    </ul></div>
    <p class="govuk-body govuk-!-margin-top-3 govuk-!-margin-bottom-1">Checkbox question</p>
    <div><ul class="govuk-list govuk-list--bullet">
      <li>Check 1</li>
      <li>Check 2</li>
    </ul></div>
    <p class="govuk-body govuk-!-margin-top-3 govuk-!-margin-bottom-1">Boolean question</p>
    <div>Yes</div>
    <p class="govuk-body govuk-!-margin-top-3 govuk-!-margin-bottom-1">Boolean list question</p>
    <div><ul class="govuk-list govuk-list--bullet">
      <li>Yes</li>
      <li>No</li>
    </ul></div>
    <p class="govuk-body govuk-!-margin-top-3 govuk-!-margin-bottom-1">Radios question</p>
    <div>Selected radio value</div>
    <p class="govuk-body govuk-!-margin-top-3 govuk-!-margin-bottom-1">Upload question</p>
    <div><a class="govuk-link" href="#">Upload question</a></div>"""
    )
    assert to_html(question) == expected


def test_to_html_returns_html_list_if_question_type_is_list(content_summary):
    list_question = content_summary.get_question("mySimpleList")
    expected = dedent(
        """\
    <ul class="govuk-list govuk-list--bullet">
      <li>Hello</li>
      <li>World</li>
    </ul>"""
    )

    assert to_html(list_question) == expected


def test_to_html_returns_html_list_if_question_type_is_boolean_list(content_summary):
    boolean_list_question = content_summary.get_question("myBooleanList")
    expected = dedent(
        """\
    <ul class="govuk-list govuk-list--bullet">
      <li>Yes</li>
      <li>No</li>
      <li>No</li>
      <li>Yes</li>
    </ul>"""
    )

    assert to_html(boolean_list_question) == expected


def test_to_html_returns_text_if_question_type_is_radios(content_summary):
    question = content_summary.get_question("myRadio")
    assert to_html(question) == "Selected radio value"


def test_to_html_returns_html_list_if_question_type_is_checkboxes(content_summary):
    integer_question = content_summary.get_question("myCheckbox")
    expected = dedent(
        """\
    <ul class="govuk-list govuk-list--bullet">
      <li>Check 1</li>
      <li>Check 2</li>
    </ul>"""
    )

    assert to_html(integer_question) == expected


def test_to_html_returns_html_text_if_question_type_is_checkboxes_and_answer_has_only_one_item(content_summary):
    question = content_summary.get_question("myCheckboxWithOneItem")

    assert to_html(question) == "check 2"


def test_to_html_returns_text_for_date_question(content_summary):
    question = content_summary.get_question("myDate")

    assert to_html(question) == "Thursday 18 February 2016"


def test_to_html_returns_text_for_pricing_question(content_summary):
    question = content_summary.get_question("myPricing")

    assert to_html(question) == "£20.41 to £25.00"


def test_to_html_returns_wrapped_anchor_if_question_type_is_upload(content_summary):
    question = content_summary.get_question("myUpload")
    assert to_html(question) == '<a class="govuk-link" href="#">Upload Question</a>'


def test_to_html_preserves_line_breaks_for_textbox_large_questions(content_summary):
    question = content_summary.get_question("myMultipleLines")
    assert to_html(question) == Markup(
        "Text with multiple lines.<br><br>This is the second line."
    )


@pytest.mark.parametrize(
    "question, expected",
    [
        ("myLowercaseText", "Text to be capitalised"),
        ("myLowercaseTextarea", "Text to be capitalised<br>with a line break."),
        (
            "myLowercaseList",
            """<ul class="govuk-list govuk-list--bullet">\n  <li>Line 1</li>\n  <li>Line 2</li>\n</ul>""",
        ),
        ("myCheckboxWithOneItem", "Check 2"),
    ],
)
def test_to_html_can_capitalize_first(content_summary, question, expected):
    question = content_summary.get_question(question)
    assert to_html(question, capitalize_first=True) == expected


@pytest.mark.parametrize(
    "question, expected",
    [
        (
            "myLinkText",
            """<a href="https://www.gov.uk" class="app-break-link" rel="external">https://www.gov.uk</a>""",
        ),
        (
            "myLinkTextarea",
            """Here is a URL:<br><br>"""
            """<a href="https://www.gov.uk" class="app-break-link" rel="external">https://www.gov.uk</a>""",
        ),
        (
            "myLinkList",
            dedent(
                """\
        <ul class="govuk-list govuk-list--bullet">
          <li><a href="https://www.gov.uk" class="app-break-link" rel="external">https://www.gov.uk</a></li>
          <li><a href="https://www.gov.uk/" class="app-break-link" rel="external">https://www.gov.uk/</a></li>
        </ul>"""
            ),
        ),
    ],
)
def test_to_html_can_format_links(content_summary, question, expected):
    question = content_summary.get_question(question)
    assert to_html(question, format_links=True) == expected


link_attributes = 'class="app-break-link" rel="external noreferrer noopener" target="_blank"'


@pytest.mark.parametrize(
    "question, expected",
    [
        (
            "myLinkText",
            f'<a href="https://www.gov.uk" {link_attributes}>https://www.gov.uk</a>'
        ),
        (
            "myLinkTextarea",
            """Here is a URL:<br><br>"""
            f'<a href="https://www.gov.uk" {link_attributes}>https://www.gov.uk</a>'
        ),
        (
            "myLinkList",
            dedent(
                f"""\
        <ul class="govuk-list govuk-list--bullet">
          <li><a href="https://www.gov.uk" {link_attributes}>https://www.gov.uk</a></li>
          <li><a href="https://www.gov.uk/" {link_attributes}>https://www.gov.uk/</a></li>
        </ul>"""
            ),
        ),
    ],
)
def test_to_html_can_format_links_which_open_in_a_new_tab(content_summary, question, expected):
    question = content_summary.get_question(question)
    assert to_html(question, format_links=True, open_links_in_new_tab=True) == expected


@pytest.mark.parametrize(
    "question, expected",
    (
        ("myUpload", """<a class="govuk-link" href="#">Upload Question</a>"""),
        ("myScriptInjection", "&lt;script&gt;do something bad&lt;/script&gt;"),
        (
            "mySimpleList",
            dedent(
                """\
        <ul class="govuk-list govuk-list--bullet">
          <li>Hello</li>
          <li>World</li>
        </ul>"""
            ),
        ),
    ),
)
@pytest.mark.parametrize("autoescape", (True, False))
def test_to_html_returns_html_which_is_safe_for_jinja(
    content_summary, question, expected, autoescape
):
    question = content_summary.get_question(question)
    html = to_html(question)

    env = jinja2.Environment(autoescape=autoescape)
    template = env.from_string("{{ html }}")

    assert template.render(html=html) == expected


def test_to_summary_list_rows(content_summary):
    questions = content_summary.sections[0].questions
    summary_list_rows = to_summary_list_rows(questions)

    assert len(summary_list_rows) == 23
    assert all("key" in row and "value" in row for row in summary_list_rows)

    assert summary_list_rows[0] == {
        "key": {"text": "Boolean question with answer True"},
        "value": {"html": Markup("Yes")},
    }

    assert summary_list_rows[12] == {
        "key": {"text": "Text question"},
        "value": {"html": Markup("Hello World")},
    }

    assert summary_list_rows[18] == {
        "key": {"text": "List question with a lower-case answer"},
        "value": {
            "html": Markup(
                dedent(
                    """\
                <ul class="govuk-list govuk-list--bullet">
                  <li>line 1</li>
                  <li>line 2</li>
                </ul>"""
                )
            )
        },
    }

    # optional_question and empty_string are empty, so should not be present
    assert "Text question with empty answer" not in [
        row["key"]["text"] for row in summary_list_rows
    ]
    assert "Optional question is not answered" not in [
        row["key"]["text"] for row in summary_list_rows
    ]


@pytest.mark.parametrize("filter_empty", [True, False])
def test_to_summary_list_rows_can_include_empty(content_summary, filter_empty):
    questions = content_summary.sections[0].questions
    summary_list_rows = to_summary_list_rows(questions, filter_empty=filter_empty)

    # optional_question and empty_string are not answered,
    # but should still be present when filter_empty is false

    text_question = [
        row for row in summary_list_rows
        if row["key"]["text"] == "Text question with empty answer"
    ]

    if filter_empty is True:
        assert text_question == []
    else:
        assert text_question == [
            {
                "key": {"text": "Text question with empty answer"},
                "value": {"html": ""},
            }
        ]

    optional_question = [
        row for row in summary_list_rows
        if row["key"]["text"] == "Optional question which is not answered"
    ]

    if filter_empty is True:
        assert optional_question == []
    else:
        assert optional_question == [
            {
                "key": {"text": "Optional question which is not answered"},
                "value": {"html": ""},
            }
        ]


def test_to_summary_list_rows_can_capitalize_first(content_summary):
    questions = content_summary.sections[0].questions
    summary_list_rows = to_summary_list_rows(questions, capitalize_first=True)

    assert summary_list_rows[4] == {
        "key": {"text": "Checkboxes question with answer that checks only one item"},
        "value": {"html": "Check 2"},
    }

    assert summary_list_rows[18] == {
        "key": {"text": "List question with a lower-case answer"},
        "value": {
            "html": Markup(
                dedent(
                    """\
                <ul class="govuk-list govuk-list--bullet">
                  <li>Line 1</li>
                  <li>Line 2</li>
                </ul>"""
                )
            )
        },
    }
