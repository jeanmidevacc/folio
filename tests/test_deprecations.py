"""Deprecated aliases kept for one release after the folio -> bulletin rename."""
from __future__ import annotations

import warnings

import pytest

import bulletin as bn

RENAMED = [
    ("Blocks", "Bulletin"),
    ("BaseBlock", "Block"),
    ("save_report", "save"),
    ("stringify_report", "stringify"),
]


@pytest.mark.parametrize(("old", "new"), RENAMED)
def test_old_name_warns_and_returns_new_object(old: str, new: str) -> None:
    with pytest.warns(DeprecationWarning, match=rf"bulletin\.{old}.*bulletin\.{new}"):
        obj = getattr(bn, old)
    assert obj is getattr(bn, new)


@pytest.mark.parametrize(("old", "new"), RENAMED)
def test_new_name_does_not_warn(old: str, new: str) -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        getattr(bn, new)


def test_unknown_attribute_still_raises_attributeerror() -> None:
    with pytest.raises(AttributeError):
        bn.DefinitelyNotAThing
