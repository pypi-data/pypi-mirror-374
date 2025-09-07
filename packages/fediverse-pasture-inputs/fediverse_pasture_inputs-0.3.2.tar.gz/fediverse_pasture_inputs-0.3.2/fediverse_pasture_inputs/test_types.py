# SPDX-FileCopyrightText: 2023-2025 Helge
#
# SPDX-License-Identifier: MIT

import pytest

from fediverse_pasture.runner.entry import Entry

from .types import InputData, Support, Details


@pytest.fixture
def input_data():
    return InputData(
        title="title",
        frontmatter="frontmatter",
        examples=[],
        filename="test.md",
        group="group",
    )


@pytest.fixture
def input_data_with_support(input_data):
    support = Support(
        title="test",
        result={
            "mastodon": lambda x: "a" + x.get("a", ""),
            "mastodon 4.2": lambda x: "b" + x.get("a", ""),
        },
    )
    input_data.support = support
    return input_data


@pytest.fixture
def input_data_with_details(input_data):
    details = Details(
        title={"activity": "activity", "other": "different"},
        extractor={
            "mastodon": lambda x: "a" + x.get("a", ""),
            "mastodon 4.2": lambda x: "b" + x.get("a", ""),
        },
    )
    input_data.details = details
    return input_data


@pytest.fixture
def entry():
    return Entry(
        {
            "activity": {"me": "some text"},
            "mastodon": {"a": "41"},
            "mastodon 4.2": {"a": "42"},
        }
    )


def test_support_for_app(input_data_with_support, entry):
    data = input_data_with_support

    assert data.support.for_app(entry, "mastodon 4.2") == "b42"
    assert data.support.for_app(entry, "mastodon") == "a41"


def test_support_with_two_arguments(input_data, entry):
    def result_func(entry, activity):
        return activity["me"] + " - " + entry["a"]

    input_data.support = Support(
        title="two arguments", result={"mastodon": result_func}
    )

    assert input_data.support.for_app(entry, "mastodon") == "some text - 41"


def test_details_extractor(input_data_with_details, entry):
    data = input_data_with_details

    assert data.details.for_app(entry, "mastodon 4.2") == "b42"
    assert data.details.for_app(entry, "mastodon") == "a41"


def test_details_title(input_data_with_details):
    assert input_data_with_details.details.title_for_app("activity") == "activity"
    assert input_data_with_details.details.title_for_app("other") == "different"
