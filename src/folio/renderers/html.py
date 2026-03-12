"""HTML rendering engine for folio reports.

Architecture
------------
- :func:`render_report` is the main entry point — it runs normalization,
  renders every block to an HTML string, then stitches everything together
  via the Jinja2 ``report.html.j2`` template.
- :func:`_render_block` is a dispatcher that routes each block type to its
  dedicated render function.
- An :class:`_IdGen` instance is threaded through every render call so that
  interactive blocks (Select, Toggle) get unique, collision-free DOM IDs.
- A pre-pass scans the block tree for Plot blocks so that library runtimes
  (e.g. plotlyjs) are embedded once in ``<head>`` rather than per-figure.
- Static assets (CSS, JS) are read from the package at import time and cached.
"""
from __future__ import annotations

import html as _html
import itertools
from datetime import datetime, timezone
from importlib.resources import files

from jinja2 import Environment, PackageLoader

from folio.blocks.asset import DataTable, Plot, Table
from folio.blocks.base import BaseBlock
from folio.blocks.data import DataDive, DataProfile
from folio.blocks.layout import Blocks, Group, Select, SelectType, Toggle, VAlign
from folio.blocks.text import Alert, BigNumber, Code, Formula, HTML, Text
from folio.renderers.datadive import render_datadive
from folio.renderers.formatting import Formatting
from folio.renderers.normalize import normalize
from folio.renderers.plot import get_runtime_scripts, render_figure, scan_for_plots
from folio.renderers.profile import render_profile
from folio.renderers.table import render_datatable, render_table

# ── package resource loading ──────────────────────────────────────────────────

_pkg = files("folio")


def _load_static(name: str) -> str:
    return (_pkg / "static" / name).read_text(encoding="utf-8")


_CSS = _load_static("report.css")
_JS = _load_static("report.js")

_jinja_env = Environment(
    loader=PackageLoader("folio", "templates"),
    autoescape=False,  # we control all HTML; user HTML goes in via safe blocks
    keep_trailing_newline=True,
)


# ── ID generator ──────────────────────────────────────────────────────────────


class _IdGen:
    """Generates sequential DOM IDs that are unique within one render pass."""

    def __init__(self) -> None:
        self._counter = itertools.count(1)

    def next(self, prefix: str = "fl") -> str:
        return f"{prefix}-{next(self._counter)}"


# ── block renderers ───────────────────────────────────────────────────────────


def _render_text(block: Text, _: _IdGen) -> str:
    from markdown_it import MarkdownIt

    md = MarkdownIt("commonmark")
    body = md.render(block.content)
    return f'<div class="fl-block fl-text">{body}</div>'


def _render_html(block: HTML, _: _IdGen) -> str:
    return f'<div class="fl-block fl-html">{block.content}</div>'


def _render_code(block: Code, _: _IdGen) -> str:
    lang = _html.escape(block.language)
    code = _html.escape(block.content)
    header = f'<div class="fl-code__header"><span>{lang}</span></div>'
    caption = (
        f'<div class="fl-code__caption">{_html.escape(block.caption)}</div>'
        if block.caption
        else ""
    )
    return (
        f'<div class="fl-block fl-code">'
        f"{header}"
        f'<pre><code class="language-{lang}">{code}</code></pre>'
        f"{caption}"
        f"</div>"
    )


def _render_formula(block: Formula, _: _IdGen) -> str:
    content = _html.escape(block.content)
    caption = (
        f'<div class="fl-formula__caption">{_html.escape(block.caption)}</div>'
        if block.caption
        else ""
    )
    return (
        f'<div class="fl-block fl-formula">'
        f'<span class="fl-formula__content">\\({content}\\)</span>'
        f"{caption}"
        f"</div>"
    )


def _render_bignumber(block: BigNumber, _: _IdGen) -> str:
    heading = _html.escape(str(block.heading))
    value = _html.escape(str(block.value))

    change_html = ""
    if block.change is not None:
        direction = "up" if block.is_upward_change else "down"
        arrow = "▲" if block.is_upward_change else "▼"
        change_html = (
            f'<div class="fl-bignumber__change fl-bignumber__change--{direction}">'
            f"{arrow} {_html.escape(block.change)}"
            f"</div>"
        )

    return (
        f'<div class="fl-block fl-bignumber">'
        f'<div class="fl-bignumber__heading">{heading}</div>'
        f'<div class="fl-bignumber__value">{value}</div>'
        f"{change_html}"
        f"</div>"
    )


def _render_alert(block: Alert, _: _IdGen) -> str:
    level = block.level.value
    title_html = (
        f'<div class="fl-alert__title">{_html.escape(block.title)}</div>'
        if block.title
        else ""
    )
    return (
        f'<div class="fl-block fl-alert fl-alert--{level}" role="alert">'
        f"{title_html}"
        f'<div class="fl-alert__message">{_html.escape(block.message)}</div>'
        f"</div>"
    )


def _render_group(block: Group, idgen: _IdGen) -> str:
    inner = "\n".join(_render_block(b, idgen) for b in block.blocks)

    if block.widths:
        cols_css = " ".join(f"{w}fr" for w in block.widths)
        style = f'style="grid-template-columns: {cols_css};"'
    else:
        style = f'style="--fl-cols: {block.columns};"'

    valign_cls = (
        f" fl-group--valign-{block.valign}" if block.valign != VAlign.TOP else ""
    )
    return f'<div class="fl-block fl-group{valign_cls}" {style}>{inner}</div>'


def _render_select(block: Select, idgen: _IdGen) -> str:
    uid = idgen.next("sel")

    if block.type == SelectType.TABS:
        tabs_html = ""
        panels_html = ""
        for i, child in enumerate(block.blocks):
            tab_id = f"{uid}-tab-{i}"
            panel_id = f"{uid}-panel-{i}"
            label = _html.escape(child.label or f"Tab {i + 1}")
            tabs_html += (
                f'<button class="fl-select__tab" role="tab" '
                f'id="{tab_id}" aria-controls="{panel_id}">'
                f"{label}</button>"
            )
            panel_html = _render_block(child, idgen)
            panels_html += (
                f'<div class="fl-select__panel" role="tabpanel" '
                f'id="{panel_id}" aria-labelledby="{tab_id}">'
                f"{panel_html}</div>"
            )
        return (
            f'<div class="fl-block fl-select" id="{uid}">'
            f'<div class="fl-select__tablist" role="tablist">{tabs_html}</div>'
            f"{panels_html}"
            f"</div>"
        )

    else:  # DROPDOWN
        options_html = ""
        panels_html = ""
        for i, child in enumerate(block.blocks):
            label = _html.escape(child.label or f"Option {i + 1}")
            options_html += f'<option value="{i}">{label}</option>'
            panel_html = _render_block(child, idgen)
            panels_html += f'<div class="fl-select__panel">{panel_html}</div>'
        return (
            f'<div class="fl-block fl-select fl-select--dropdown" id="{uid}">'
            f'<select class="fl-select__select" aria-label="Select view">'
            f"{options_html}</select>"
            f"{panels_html}"
            f"</div>"
        )


def _render_toggle(block: Toggle, idgen: _IdGen) -> str:
    uid = idgen.next("tog")
    label = _html.escape(block.label or "Details")
    inner = "\n".join(_render_block(b, idgen) for b in block.blocks)
    chevron = (
        '<svg class="fl-toggle__icon" width="16" height="16" viewBox="0 0 20 20" '
        'fill="currentColor" aria-hidden="true">'
        '<path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938'
        "a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 "
        '01.02-1.06z" clip-rule="evenodd"/></svg>'
    )
    return (
        f'<div class="fl-block fl-toggle" id="{uid}">'
        f'<button class="fl-toggle__header" aria-expanded="false" '
        f'aria-controls="{uid}-body">'
        f"<span>{label}</span>{chevron}"
        f"</button>"
        f'<div class="fl-toggle__body" id="{uid}-body" hidden>{inner}</div>'
        f"</div>"
    )


def _render_plot(block: Plot, _: _IdGen) -> str:
    return render_figure(block)


def _render_table(block: Table, _: _IdGen) -> str:
    return render_table(block)


def _render_datatable(block: DataTable, _: _IdGen) -> str:
    return render_datatable(block)


def _render_profile(block: DataProfile, _: _IdGen) -> str:
    return render_profile(block)


def _render_datadive(block: DataDive, _: _IdGen) -> str:
    return render_datadive(block)


def _render_placeholder(block: BaseBlock, _: _IdGen) -> str:
    name = _html.escape(type(block).__name__)
    return (
        f'<div class="fl-block fl-placeholder">'
        f"⚙ <strong>{name}</strong> — rendering implemented in a later phase."
        f"</div>"
    )


# ── dispatcher ────────────────────────────────────────────────────────────────

_DISPATCH: dict[type, object] = {
    Text: _render_text,
    HTML: _render_html,
    Code: _render_code,
    Formula: _render_formula,
    BigNumber: _render_bignumber,
    Alert: _render_alert,
    Group: _render_group,
    Select: _render_select,
    Toggle: _render_toggle,
    Plot: _render_plot,
    Table: _render_table,
    DataTable: _render_datatable,
    DataProfile: _render_profile,
    DataDive: _render_datadive,
}


def _render_block(block: BaseBlock, idgen: _IdGen) -> str:
    if isinstance(block, Blocks):
        inner = "\n".join(_render_block(b, idgen) for b in block.blocks)
        return f'<div class="fl-blocks">{inner}</div>'

    renderer = _DISPATCH.get(type(block))
    if renderer is not None:
        return renderer(block, idgen)  # type: ignore[call-arg]

    return _render_placeholder(block, idgen)


# ── public API ────────────────────────────────────────────────────────────────


def render_report(
    blocks: Blocks,
    name: str = "Report",
    formatting: Formatting | None = None,
) -> str:
    """Render *blocks* to a fully self-contained HTML string."""
    fmt = formatting or Formatting()
    normalised = normalize(blocks)

    # Pre-pass: detect which library runtimes are needed and build <head> scripts.
    libraries = scan_for_plots(normalised)
    head_scripts = get_runtime_scripts(libraries)

    idgen = _IdGen()
    content_html = _render_block(normalised, idgen)

    now = datetime.now(tz=timezone.utc)
    template = _jinja_env.get_template("report.html.j2")

    return template.render(
        report_name=name,
        report_date=now.strftime("%Y-%m-%d %H:%M UTC"),
        report_date_iso=now.isoformat(),
        css_vars=fmt.to_css_vars(),
        report_css=_CSS,
        report_js=_JS,
        head_scripts=head_scripts,
        content_html=content_html,
        show_header=name != "Report",
    )


__all__ = ["render_report"]
