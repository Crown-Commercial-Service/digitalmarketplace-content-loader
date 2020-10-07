import markdown

from dmcontent.markdown import GOVUKFrontendExtension


class TestGOVUKFrontendExtension:
    def test_is_python_markdown_extension(self):
        assert markdown.Markdown(extensions=[GOVUKFrontendExtension()])

    def test_it_adds_govuk_design_system_styles(self):
        text = """
## Headings

1. ordered lists

Paragraphs, and [links](#).

- bullet lists
"""

        assert (
            markdown.markdown(text, extensions=[GOVUKFrontendExtension()])
            == """<h2 class="govuk-heading-m">Headings</h2>
<ol class="govuk-list govuk-list--number">
<li>ordered lists</li>
</ol>
<p class="govuk-body">Paragraphs, and <a class="govuk-link" href="#">links</a>.</p>
<ul class="govuk-list govuk-list--bullet">
<li>bullet lists</li>
</ul>"""
        )

    def test_it_does_not_change_existing_html(self):
        text = '<a href="#" target="_blank" rel="noopener noreferrer">link (opens in new tab)</a>'

        assert text in markdown.markdown(text, extensions=[GOVUKFrontendExtension()])
