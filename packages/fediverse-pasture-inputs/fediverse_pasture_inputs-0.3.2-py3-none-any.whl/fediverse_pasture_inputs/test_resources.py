from . import available
from .config import used_resources, check_resources


def test_resources():
    assert len(available) > 0
    assert len(used_resources) > 0

    check_resources()
