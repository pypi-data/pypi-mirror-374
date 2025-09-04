# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 Helge
#
# SPDX-License-Identifier: MIT

from fediverse_pasture_inputs.config import resource_path
from fediverse_pasture_inputs.types import InputData, Details, Support

from fediverse_pasture_inputs.utils import format_as_json

emoji_examples = [
    {
        "content": "emoji base properties :cow1:",
        "tag": [
            {
                "type": "Emoji",
                "name": ":cow1:",
                "updated": "2025-01-22T12:57:33Z",
                "icon": {
                    "type": "Image",
                    "mediaType": "image/png",
                    "url": resource_path("cow_emoji.png"),
                },
            },
        ],
    },
    {
        "content": "emoji minimal properties :cow2:",
        "tag": [
            {
                "type": "Emoji",
                "name": ":cow2:",
                "icon": {
                    "url": resource_path("cow_emoji.png"),
                },
            },
        ],
    },
    {
        "content": "emoji with type of icon :cow3:",
        "tag": [
            {
                "type": "Emoji",
                "name": ":cow3:",
                "icon": {
                    "type": "Image",
                    "url": resource_path("cow_emoji.png"),
                },
            },
        ],
    },
    {
        "content": "emoji with inlined icon :cow4:",
        "tag": [
            {
                "type": "Emoji",
                "name": ":cow4:",
                "icon": resource_path("cow_emoji.png"),
            },
        ],
    },
    {
        "content": "emoji with id :cow5:",
        "tag": [
            {
                "id": resource_path("cow_emoji.jsonap"),
                "type": "Emoji",
                "name": ":cow5:",
                "updated": "2025-01-22T12:57:33Z",
                "icon": {
                    "type": "Image",
                    "mediaType": "image/png",
                    "url": resource_path("cow_emoji.png"),
                },
            },
        ],
    },
    {
        "content": "emoji with missing icon :cow6:",
        "tag": [
            {
                "type": "Emoji",
                "name": ":cow6:",
            },
        ],
    },
    {
        "content": "emoji just id :cow:",
        "tag": [
            resource_path("cow_emoji.jsonap"),
        ],
    },
]

details = Details(
    title={"mastodon": "| tag | emojis | Example |"},
    extractor={
        "activity": lambda x: format_as_json(x.get("object", {}).get("tag")),
        "mastodon": lambda x: format_as_json(x.get("emojis")),
    },
)


def format_emoji(obj):
    if obj is None:
        return "❌"
    emojis = obj.get("emojis")
    if len(emojis) > 0:
        return "✅"

    return "-"


support = Support(
    title="content",
    result={
        "activity": lambda x: x.get("object", {}).get("content"),
        "mastodon": format_emoji,
    },
)

data = InputData(
    title="Emoji",
    frontmatter="""
Emojis are documented in [FEP-9098](https://codeberg.org/fediverse/fep/src/branch/main/fep/9098/fep-9098.md)

In the support table:     

- ✅ means Emoji parsed
- - means Emoji not parsed
- ❌ failed to process, i.e. no message received in the application.
    """,
    filename="emoji.md",
    examples=emoji_examples,
    group="Object Content",
    details=details,
    support=support,
)
