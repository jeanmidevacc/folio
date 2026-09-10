"""The briefing.lab boundary: registration + on-demand asset injection."""
from __future__ import annotations

import datetime

import pandas as pd
import pytest

import briefing as bf
from briefing.renderers.registry import asset_js_for, lookup_renderer

_NOW = datetime.datetime(2020, 1, 1)
_LAB_JS_MARKER = "briefing.lab — DataDive interactive dot explorer"


@pytest.fixture()
def df() -> pd.DataFrame:
    return pd.DataFrame(
        {"a": [1, 2, 3, 4], "b": [4.0, 3.0, 2.0, 1.0], "g": ["x", "y", "x", "y"]}
    )


def test_lab_blocks_have_registered_renderers(df: pd.DataFrame) -> None:
    assert lookup_renderer(bf.lab.DataProfile(df)) is not None
    assert lookup_renderer(bf.lab.DataDive(df)) is not None


def test_only_datadive_carries_a_js_asset(df: pd.DataFrame) -> None:
    assert asset_js_for(bf.lab.DataDive(df)) is not None
    assert asset_js_for(bf.lab.DataProfile(df)) is None
    assert asset_js_for(bf.Text("# plain")) is None


def test_core_report_does_not_inline_the_lab_engine(df: pd.DataFrame) -> None:
    html = bf.stringify(bf.Briefing(bf.Text("# hi"), bf.Table(df)), now=_NOW)
    assert _LAB_JS_MARKER not in html


def test_profile_only_report_does_not_inline_the_lab_engine(df: pd.DataFrame) -> None:
    html = bf.stringify(bf.Briefing(bf.lab.DataProfile(df)), now=_NOW)
    assert _LAB_JS_MARKER not in html


def test_datadive_report_inlines_the_lab_engine_exactly_once(df: pd.DataFrame) -> None:
    html = bf.stringify(
        bf.Briefing(bf.lab.DataDive(df, x="a", y="b"), bf.lab.DataDive(df, x="a", y="b")),
        now=_NOW,
    )
    assert html.count(_LAB_JS_MARKER) == 1


def test_datadive_nested_in_a_container_still_triggers_injection(df: pd.DataFrame) -> None:
    html = bf.stringify(
        bf.Briefing(bf.Group(bf.Text("# g"), bf.lab.DataDive(df, x="a", y="b"))),
        now=_NOW,
    )
    assert _LAB_JS_MARKER in html


def test_output_is_still_byte_reproducible_with_lab_blocks(df: pd.DataFrame) -> None:
    report = bf.Briefing(bf.lab.DataProfile(df), bf.lab.DataDive(df, x="a", y="b"))
    assert bf.stringify(report, now=_NOW) == bf.stringify(report, now=_NOW)
