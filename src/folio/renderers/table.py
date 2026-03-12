"""Table block rendering — static Table and interactive DataTable.

Table
-----
Renders a pandas DataFrame or Styler as a styled static HTML table.
If the user passes a Styler, its inline CSS is preserved verbatim;
otherwise a plain ``<table>`` is emitted with folio's own table CSS.

DataTable
---------
Renders a DataFrame as a fully self-contained interactive table with:
- Live search / filter (all columns)
- Click-to-sort columns (auto-detects numeric vs text)
- Client-side pagination (25 rows per page)

All interaction is handled by vanilla JS in ``report.js``; the rendered
HTML contains the full data set, so the table works offline forever.
"""
from __future__ import annotations

import html as _html
import typing as t

from folio._error import FolioError

if t.TYPE_CHECKING:
    from folio.blocks.asset import DataTable, Table


# ── helpers ───────────────────────────────────────────────────────────────────


def _fmt(val: t.Any) -> str:
    """Format a single cell value to a display string."""
    try:
        import pandas as pd

        if pd.isna(val):
            return ""
    except (TypeError, ValueError, ImportError):
        pass
    if isinstance(val, float):
        if val == int(val) and abs(val) < 1e15:
            return str(int(val))
        return f"{val:g}"
    return str(val)


def _use_index(df: t.Any) -> bool:
    """Return True if the DataFrame index should be rendered as a column."""
    import pandas as pd

    return not isinstance(df.index, pd.RangeIndex) or df.index.name is not None


# ── static Table ──────────────────────────────────────────────────────────────


def render_table(block: Table) -> str:
    """Render a :class:`~folio.Table` block to a static HTML table fragment."""
    try:
        import pandas as pd
        from pandas.io.formats.style import Styler
    except ImportError as exc:
        raise FolioError("Table requires pandas — install it with: pip install pandas") from exc

    data = block.data

    if isinstance(data, Styler):
        # Styler.to_html() returns a full <style>+<table> fragment; use it as-is.
        table_html = data.to_html()
    else:
        table_html = data.to_html(
            classes="fl-table__table",
            border=0,
            index=_use_index(data),
        )

    caption_html = (
        f'<div class="fl-table__caption">{_html.escape(block.caption)}</div>'
        if block.caption
        else ""
    )
    return (
        f'<div class="fl-block fl-table">'
        f'<div class="fl-table__scroll">{table_html}</div>'
        f"{caption_html}"
        f"</div>"
    )


# ── interactive DataTable ─────────────────────────────────────────────────────


def render_datatable(block: DataTable) -> str:
    """Render a :class:`~folio.DataTable` block to an interactive HTML table."""
    df = block.df
    show_index = _use_index(df)

    # ── header ──
    header_cells = ""
    col_idx = 0
    if show_index:
        idx_name = _html.escape(str(df.index.name or ""))
        header_cells += (
            f'<th class="fl-dt__th" data-col="{col_idx}" scope="col">'
            f"<span>{idx_name}</span>"
            f'<span class="fl-dt__sort-icon" aria-hidden="true"></span>'
            f"</th>"
        )
        col_idx += 1
    for col in df.columns:
        header_cells += (
            f'<th class="fl-dt__th" data-col="{col_idx}" scope="col">'
            f"<span>{_html.escape(str(col))}</span>"
            f'<span class="fl-dt__sort-icon" aria-hidden="true"></span>'
            f"</th>"
        )
        col_idx += 1

    # ── rows ──
    rows_html = ""
    for idx_val, row in zip(df.index, df.itertuples(index=False)):
        cells = ""
        if show_index:
            cells += f"<td>{_html.escape(_fmt(idx_val))}</td>"
        for val in row:
            cells += f"<td>{_html.escape(_fmt(val))}</td>"
        rows_html += f"<tr>{cells}</tr>"

    caption_html = (
        f'<div class="fl-dt__caption">{_html.escape(block.caption)}</div>'
        if block.caption
        else ""
    )
    return (
        f'<div class="fl-block fl-datatable">'
        f'<div class="fl-dt__toolbar">'
        f'<input class="fl-dt__search" type="search" placeholder="Search…" aria-label="Search table" />'
        f'<span class="fl-dt__count"></span>'
        f"</div>"
        f'<div class="fl-dt__scroll">'
        f'<table class="fl-dt__table">'
        f"<thead><tr>{header_cells}</tr></thead>"
        f"<tbody>{rows_html}</tbody>"
        f"</table>"
        f"</div>"
        f'<div class="fl-dt__footer">'
        f'<button class="fl-dt__page-btn" data-dir="-1">&#8592; Prev</button>'
        f'<span class="fl-dt__page-info"></span>'
        f'<button class="fl-dt__page-btn" data-dir="1">Next &#8594;</button>'
        f"</div>"
        f"{caption_html}"
        f"</div>"
    )


__all__ = ["render_datatable", "render_table"]
