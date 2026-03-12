"""Asset-based blocks: Plot, Table, DataTable.

These blocks hold external data (figures, DataFrames) and are serialised
into the HTML as inline assets during the render pass.

Phase 3 (Plot) and Phase 4 (Table / DataTable) implement the full rendering.
The classes here define the public API surface so they can be used and tested
for construction / wrapping even before rendering is implemented.
"""
from __future__ import annotations

import typing as t

from folio._error import FolioError
from folio.blocks.base import BaseBlock, BlockId, _MAX_CAPTION_LEN, _truncate

if t.TYPE_CHECKING:
    import pandas as pd
    from pandas.io.formats.style import Styler


class Plot(BaseBlock):
    """Chart / figure block — library agnostic.

    Auto-detects the figure type at render time:
    - **Plotly** → embedded as interactive HTML (inline JS)
    - **Altair / Vega-Lite** → embedded as Vega spec (inline runtime)
    - **Matplotlib / Seaborn / Plotnine** → embedded as inline SVG
    - **Bokeh** → embedded with inline resources

    Example::

        fl.Plot(plotly_fig, caption="Revenue over time")
        fl.Plot(altair_chart, label="Chart", responsive=True)
    """

    def __init__(
        self,
        figure: t.Any,
        caption: str | None = None,
        responsive: bool = True,
        scale: float = 1.0,
        name: BlockId | None = None,
        label: str | None = None,
    ) -> None:
        super().__init__(name=name, label=label)
        self.figure = figure
        self.caption = _truncate(caption, _MAX_CAPTION_LEN) if caption else caption
        self.responsive = responsive
        self.scale = scale


class Table(BaseBlock):
    """Static HTML table rendered from a pandas DataFrame or Styler.

    Best for multidimensional DataFrames where you want pandas' Styler
    formatting to be preserved.

    Example::

        fl.Table(df)
        fl.Table(df.style.highlight_max(color="lightgreen"))
    """

    def __init__(
        self,
        data: pd.DataFrame | Styler,
        caption: str | None = None,
        name: BlockId | None = None,
        label: str | None = None,
    ) -> None:
        try:
            import pandas as pd
        except ImportError as exc:
            raise FolioError("Table requires pandas — install it with: pip install pandas") from exc

        super().__init__(name=name, label=label)
        self.data = data
        self.caption = _truncate(caption, _MAX_CAPTION_LEN) if caption else caption


class DataTable(BaseBlock):
    """Interactive, sortable and searchable table rendered from a pandas DataFrame.

    Handles large datasets via client-side pagination. Viewers can also sort
    columns and filter rows by typing in the search box.

    Example::

        fl.DataTable(df, caption="Top 1 000 orders")
    """

    #: Maximum rows rendered by default; larger DataFrames are truncated with a warning.
    MAX_ROWS: t.ClassVar[int] = 10_000

    def __init__(
        self,
        df: pd.DataFrame,
        caption: str | None = None,
        max_rows: int = MAX_ROWS,
        name: BlockId | None = None,
        label: str | None = None,
    ) -> None:
        try:
            import pandas as pd
        except ImportError as exc:
            raise FolioError(
                "DataTable requires pandas — install it with: pip install pandas"
            ) from exc

        import warnings

        super().__init__(name=name, label=label)

        if len(df) > max_rows:
            warnings.warn(
                f"DataTable: DataFrame has {len(df):,} rows — truncating to {max_rows:,}. "
                "Increase 'max_rows' to render more.",
                stacklevel=2,
            )
            df = df.head(max_rows)

        self.df = df
        self.caption = _truncate(caption, _MAX_CAPTION_LEN) if caption else caption
        self.max_rows = max_rows


# ── public re-exports ─────────────────────────────────────────────────────────

__all__: list[str] = ["DataTable", "Plot", "Table"]
