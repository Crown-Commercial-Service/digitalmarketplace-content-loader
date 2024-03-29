from typing import Mapping
from xml.etree.ElementTree import Element

from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor


class _ClassAddingTreeprocessor(Treeprocessor):
    _mapping: Mapping[str, str]

    def __init__(self, mapping: Mapping[str, str]):
        self._mapping = mapping

    def run(self, root: Element):
        self._run(root)

    def _run(self, element: Element):
        # recurse
        for child in element:
            self._run(child)

        # mutate each affected element in-place
        if element.tag in self._mapping:
            if not self.is_html_placeholder(element):
                orig_class = element.attrib.get("class", "")
                element.set("class", (orig_class + " " if orig_class else "") + self._mapping[element.tag])

    def is_html_placeholder(self, element: Element):
        """Check if this element is one that's been added as a placeholder for some raw html by
        markdown.preprocessors.HtmlBlockPreprocessor."""
        placeholders = [self.md.htmlStash.get_placeholder(i) for i in range(self.md.htmlStash.html_counter)]
        return element.tag == "p" and element.text in placeholders


class GOVUKFrontendExtension(Extension):
    """
    Markdown extension adding govuk-frontend classes to generated paragraphs and lists (note - will not affect
    manual html)
    """
    GOVUK_ELEMENT_CLASSES = {
        "p": "govuk-body",
        "ul": "govuk-list govuk-list--bullet",
        "ol": "govuk-list govuk-list--number",
        "a": "govuk-link",
        "h2": "govuk-heading-m",
        "h3": "govuk-heading-s",
    }

    def extendMarkdown(self, md, md_globals):
        # NOTE the interface for registering extensions is much improved after Markdown 3.0.0. TODO upgrade.
        md.registerExtension(self)
        self.processor = _ClassAddingTreeprocessor(self.GOVUK_ELEMENT_CLASSES)
        self.processor.md = md
        md.treeprocessors["govukfrontendclassadder"] = self.processor
