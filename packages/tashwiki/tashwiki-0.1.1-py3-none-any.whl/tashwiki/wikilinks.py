""" Customised wikilinks extension

Based on markdown.extensions.wikilinks
"""

import re
import xml.etree.ElementTree as etree
from typing import Any

from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor

from tashwiki.utils import label_to_page_name


def build_html_class(page):
    return ""


class WikiLinkExtension(Extension):
    """ Add inline processor to Markdown. """

    def __init__(self, **kwargs):
        """ Default configuration options. """
        self.config = {
            "base_url": ["/", "String to append to beginning or URL."],
            "end_url": ["/", "String to append to end of URL."],
            "html_class": [build_html_class, "Callback to return actual html class"],
        }
        super().__init__(**kwargs)

    def extendMarkdown(self, md):
        self.md = md

        # append to end of inline patterns
        WIKILINK_RE = r"\[\[([\(\)\w0-9_ -]+?)(?:\|([^\]]+?))?\]\]"
        wikilinkPattern = WikiLinksInlineProcessor(WIKILINK_RE, self.getConfigs())
        wikilinkPattern.md = md
        md.inlinePatterns.register(wikilinkPattern, "wikilink", 75)


class WikiLinksInlineProcessor(InlineProcessor):
    """ Build link from `wikilink`. """

    def __init__(self, pattern: str, config: dict[str, Any]):
        super().__init__(pattern)
        self.config = config

    def build_url(self, label: str) -> str:
        return "{}{}{}".format(
            self.config["base_url"],
            label,
            self.config["end_url"],
        )

    def handleMatch(self, m: re.Match[str], data: str) -> tuple[etree.Element | str, int, int]:
        if page := m.group(1).strip():
            label = m.group(2).strip() if m.group(2) else page
            url = self.build_url(label_to_page_name(page))
            a = etree.Element("a")
            a.text = label
            a.set("href", url)
            html_class = self.config["html_class"]
            if html_class:
                a.set("class", html_class(page))
        else:
            a = ""
        return a, m.start(0), m.end(0)
