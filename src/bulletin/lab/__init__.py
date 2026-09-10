"""``bulletin.lab`` — custom-visualisation blocks.

These are richer, more opinionated visualisations kept out of the core grammar
so it stays small and dependency-free:

* :class:`DataProfile` — per-column statistics with inline SVG mini-charts.
* :class:`DataDive` — Facets Dive-style interactive dot explorer.

Install with ``pip install bulletin[lab]``. Importing this module registers the
blocks with the renderer, so ``bulletin.stringify``/``bulletin.save`` can render
them once it has been imported (``bulletin`` imports it automatically when it is
importable).

Usage::

    import bulletin as bn

    bn.save(
        bn.Bulletin(
            bn.lab.DataProfile(df),
            bn.lab.DataDive(df, x="revenue", y="margin", color="region"),
        ),
        "report.html",
    )
"""
from __future__ import annotations

from importlib.resources import files

from bulletin.lab._blocks import DataDive, DataProfile
from bulletin.lab._render_datadive import render_datadive
from bulletin.lab._render_profile import render_profile
from bulletin.renderers.registry import IdGen, register_renderer

_LAB_JS = (files("bulletin.lab") / "static" / "lab.js").read_text(encoding="utf-8")


def _render_profile_block(block: DataProfile, _: IdGen) -> str:
    return render_profile(block)


def _render_datadive_block(block: DataDive, _: IdGen) -> str:
    return render_datadive(block)


register_renderer(DataProfile, _render_profile_block)
register_renderer(DataDive, _render_datadive_block, js_asset=_LAB_JS)

__all__ = ["DataDive", "DataProfile"]
