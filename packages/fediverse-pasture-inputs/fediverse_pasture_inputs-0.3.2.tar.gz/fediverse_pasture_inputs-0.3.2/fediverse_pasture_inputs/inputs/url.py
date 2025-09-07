# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 Helge
#
# SPDX-License-Identifier: MIT

from bovine.activitystreams.utils import as_list

from fediverse_pasture_inputs.types import InputData, Details, Support
from fediverse_pasture_inputs.utils import pre_format, escape_markdown, format_as_json

link_html = {
    "type": "Link",
    "mediaType": "text/html",
    "href": "http://html.example/objects/123",
}

link_video = {
    "type": "Link",
    "mediaType": "video/mp4",
    "href": "http://video.example/objects/123",
}


url_examples = [
    "http://remote.example/objects/123",
    ["http://remote.example/objects/123"],
    ["http://remote.example/objects/123", "http://other.example/objects/123"],
    ["http://other.example/objects/123", "http://remote.example/objects/123"],
    link_html,
    link_video,
    ["http://remote.example/objects/123", link_html],
    [link_html, "http://remote.example/objects/123"],
    [link_html, link_video],
    [link_video, link_html],
    [link_video, {**link_html, "rel": "canonical"}],
    {"href": "https://notype.example/"},
]

examples_with_comment = [
    {
        "content": "See https://codeberg.org/funfedidev/fediverse-pasture-inputs/issues/66",
        "url": "http://pasture-one-actor/objects/123",
    }
]

details = Details(
    extractor={
        "activity": lambda x: format_as_json(x.get("object", {}).get("url")),
        "mastodon": lambda x: pre_format(x.get("url")),
        "misskey": lambda x: pre_format(escape_markdown(x.get("url"))),
    },
    title={
        "mastodon": "| url | url | Example |",
        "misskey": "| url | url | Example |",
    },
)


def url_count_in_activity(x):
    obj = x.get("object", {})
    url = obj.get("url")
    if isinstance(url, str):
        return "string"
    if isinstance(url, dict):
        return "dict"

    return f"List with {len(url)} elements"


def number_agrees(x, activity={}):
    if x is None or len(x) == 0:
        return "❌"
    obj = activity.get("object", {})
    url_count = len(as_list(obj.get("url", [])))
    result = len(as_list(x.get("url")))

    if url_count == result:
        return "✅"

    return f"{result}/{url_count}"


support = Support(
    title="Number of links",
    result={"activity": url_count_in_activity, "mastodon": number_agrees},
)

data = InputData(
    title="Url Parameter",
    frontmatter="""Here we analyze varying [url parameters](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-url).
The usage examples are inspired by Peertube's usage, see
[their documentation](https://docs.joinpeertube.org/api/activitypub#video).

The support table just compares the number of links at the momment. ❌ means failed to parse. 
✅ means all links present.

""",
    filename="url.md",
    group="Object Properties",
    examples=[{"content": "text", "url": url} for url in url_examples]
    + examples_with_comment,
    details=details,
    support=support,
)
