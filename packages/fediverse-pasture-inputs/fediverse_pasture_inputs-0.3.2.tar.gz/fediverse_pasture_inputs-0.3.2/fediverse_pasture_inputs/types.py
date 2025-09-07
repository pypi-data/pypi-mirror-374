# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 Helge
#
# SPDX-License-Identifier: MIT

import os
from dataclasses import dataclass, field
from typing import Dict, Callable, List
from warnings import deprecated

from fediverse_pasture.runner.entry import Entry
from .utils import value_from_dict_for_app


def to_docs_path(filename):
    return os.path.join("../../site/docs/support_tables/generated", filename)


SupportFunction = Callable[[dict], str] | Callable[[dict, dict], str]
"""Type of function to assigned in support result. Examples

```python
def result(entry):
    return "something"

def result(entry, activity):
    return "something"
```

See [fediverse_pasture_inputs.types.Support.for_app][] for details.
"""


@dataclass
class Support:
    """Configuration for the support table"""

    title: str = field(metadata={"description": "The title of the support"})
    result: dict[str, SupportFunction] = field(
        metadata={"description": "Mapping betweeen applications and the support result"}
    )

    def for_app(self, entry: Entry, app: str):
        """Returns the support result for the entry and app"""
        extractor = value_from_dict_for_app(self.result, app)

        data = entry.entry.get(app)
        if extractor.__code__.co_argcount == 2:
            activity = entry.entry.get("activity")
            return extractor(data, activity)

        return extractor(data)


@dataclass
class Details:
    """Configuration for the details table"""

    title: dict[str, str] = field(metadata={"description": "The title line per app"})
    extractor: Dict[str, Callable[[Dict], List[str]]] = field(
        metadata={
            "description": "map of application / activity to the corresponding display in the details table"
        }
    )
    frontmatter: str | None = field(
        default=None,
        metadata={"description": "optional frontmatter to display before the details"},
    )

    def for_app(self, entry: Entry, app: str):
        """Returns the support result for the entry and app"""
        extractor = value_from_dict_for_app(self.extractor, app, default=["❌"])
        data = entry.entry.get(app)
        return extractor(data)

    def title_for_app(self, app: str):
        """Returns the title line for the app"""
        return value_from_dict_for_app(self.title, app)


@dataclass
class InputData:
    """Dataclass describing an input for an object support table"""

    title: str = field(metadata={"description": "Title of the support table"})
    frontmatter: str = field(
        metadata={"description": "Frontmatter describing why the support table exists"}
    )
    examples: List[Dict] = field(
        metadata={"description": "List of dictionaries being added to the object"}
    )
    filename: str = field(metadata={"description": "Name of generated markdown file"})
    group: str = field(
        metadata={"description": "The group the example is to be displayed in"}
    )

    details: Details | None = field(
        default=None,
        metadata={"description": "How the details table will be generated"},
    )
    support: Support | None = field(
        default=None,
        metadata={"description": "If set, how the support table should be build"},
    )

    @property
    def docs_path(self):
        return to_docs_path(self.filename)

    @deprecated("Deprecated use .support.for_app instead")
    def support_for_app(self, entry: Entry, app: str):
        if not self.support:
            raise ValueError("Support not available")
        return self.support.for_app(entry, app)

    @deprecated("Deprecated use .details.for_app instead")
    def detail_for_app(self, entry: Entry, app: str):
        if not self.details:
            raise ValueError("Details not available")
        extractor = value_from_dict_for_app(self.details.extractor, app, default=["❌"])
        data = entry.entry.get(app)
        return extractor(data)

    @deprecated("Deprecated use .details.title_for_app instead")
    def detail_title_for_app(self, app: str):
        if not self.details:
            raise ValueError("Details not available")
        return value_from_dict_for_app(self.details.title, app)
