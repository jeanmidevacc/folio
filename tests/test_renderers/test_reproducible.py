"""Rendering is byte-reproducible when the timestamp is pinned."""
from __future__ import annotations

from datetime import UTC, datetime

import bulletin as bn
from bulletin.renderers.html import render_report


def _doc() -> bn.Bulletin:
    return bn.Bulletin(
        bn.Text("# Title"),
        bn.Group(bn.BigNumber("A", 1), bn.BigNumber("B", 2), columns=2),
        bn.Alert("note", level="info"),
    )


def test_same_input_same_output_with_pinned_now() -> None:
    now = datetime(2024, 1, 2, 3, 4, tzinfo=UTC)
    a = render_report(_doc(), name="R", now=now)
    b = render_report(_doc(), name="R", now=now)
    assert a == b


def test_pinned_now_appears_in_header() -> None:
    now = datetime(2024, 1, 2, 3, 4, tzinfo=UTC)
    html = render_report(_doc(), name="R", now=now)
    assert "2024-01-02 03:04 UTC" in html
    assert now.isoformat() in html


def test_source_date_epoch_env_var(monkeypatch) -> None:
    # 2021-01-01T00:00:00Z
    monkeypatch.setenv("SOURCE_DATE_EPOCH", "1609459200")
    html = render_report(_doc(), name="R")
    assert "2021-01-01 00:00 UTC" in html


def test_unpinned_still_renders() -> None:
    assert "<html" in render_report(_doc(), name="R")
