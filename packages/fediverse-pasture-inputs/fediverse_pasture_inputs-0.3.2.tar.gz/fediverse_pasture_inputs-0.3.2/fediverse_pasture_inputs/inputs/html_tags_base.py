# SPDX-FileCopyrightText: 2025 Helge
#
# SPDX-License-Identifier: MIT

from fediverse_pasture_inputs.types import InputData, Details, Support
from fediverse_pasture_inputs.utils import (
    pre_format,
    escape_markdown,
    pre_wrapped,
    with_tooltip,
)


html_tags = [
    "<b>bold</b>",
    "<strong>strong</strong>",
    "<i>italic</i>",
    "<em>emphasis</em>",
    "<s>stricken</s>",
    "<ol><li>ordered</li></ol>",
    "<ul><li>unordered</li></ul>",
    "<h1>h1</h1>",
    "<h2>h2</h2>",
    "<h3>h3</h3>",
    "<h4>h4</h4>",
    "<h5>h5</h5>",
    "<code>code</code>",
    "<pre>pre</pre>",
    "<blockquote>blockquote</blockquote>",
    "line<br>break",
    "<p>paragraph</p>",
    "<small>small</small>",
    "<sup>sup</sup>",
    "<sub>sub</sub>",
]

details = Details(
    extractor={
        "activity": lambda x: pre_format(
            x.get("object", {}).get("content"), pre_wrap=True
        ),
        "mastodon": lambda x: pre_format(x.get("content"), pre_wrap=True),
        "misskey": lambda x: pre_format(escape_markdown(x.get("text")), pre_wrap=True),
    },
    title={
        "mastodon": "| content | content | Example |",
        "misskey": "| content | text | Example |",
    },
)


def mastodon_support(entry: dict, activity: dict = {}):
    if entry is None or len(entry) == 0:
        return "❌"

    content = activity.get("object", {}).get("content")
    entry_content = entry.get("content")

    if content == entry_content:
        return "✅"

    return with_tooltip("❓", entry_content)


support = Support(
    title="content",
    result={
        "activity": lambda x: pre_wrapped(x.get("object", {}).get("content"), False),
        "misskey": lambda x: with_tooltip("❓", x.get("text")),
        "mastodon": mastodon_support,
    },
)

data = InputData(
    title="Basic HTML tags",
    frontmatter="""Here we analyze, which types
of HTML tags are allowed inside the content field. Sanitizing fields is
desired behavior as seen in [Section B.10 of ActivityPub](https://www.w3.org/TR/activitypub/#security-sanitizing-content).

The ✅ means that the html tag was left unchanged. ❓ indicates the content was changed,
by hovering over it, one can see into what.

❓ for misskey is due us not supporting checking markdown yet.
""",
    filename="html_tags_base.md",
    group="HTML Tags",
    examples=[{"content": content} for content in html_tags],
    details=details,
    support=support,
)
