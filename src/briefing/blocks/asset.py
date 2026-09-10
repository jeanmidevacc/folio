"""Asset-based blocks: Plot, Table, DataTable.

These blocks hold external data (figures, DataFrames) and are serialised
into the HTML as inline assets during the render pass.

``Table`` / ``DataTable`` accept any dataframe library ``briefing`` can
normalise (see :mod:`briefing._frames`); the data is stored internally as a
pandas DataFrame.
"""
from __future__ import annotations

import typing as t
import warnings

from briefing._frames import is_pandas_dataframe, to_pandas
from briefing.blocks.base import _MAX_CAPTION_LEN, Block, BlockId, _truncate

if t.TYPE_CHECKING:
    import pandas as pd
    from pandas.io.formats.style import Styler


class Plot(Block):
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


class Table(Block):
    """Static HTML table rendered from a dataframe or a pandas Styler.

    Best for multidimensional DataFrames where you want pandas' Styler
    formatting to be preserved. A Styler is used verbatim; any other frame
    (pandas, polars, pyarrow, …) is normalised to pandas.

    Example::

        bf.Table(df)
        bf.Table(df.style.highlight_max(color="lightgreen"))
    """

    def __init__(
        self,
        data: pd.DataFrame | Styler | t.Any,
        caption: str | None = None,
        name: BlockId | None = None,
        label: str | None = None,
    ) -> None:
        super().__init__(name=name, label=label)
        # A Styler carries its own formatting rules — keep it as-is. Everything
        # else goes through the dataframe intake layer.
        if type(data).__name__ == "Styler" or is_pandas_dataframe(data):
            self.data = data
        else:
            self.data = to_pandas(data, block="Table")
        self.caption = _truncate(caption, _MAX_CAPTION_LEN) if caption else caption


class DataTable(Block):
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
        df: pd.DataFrame | t.Any,
        caption: str | None = None,
        max_rows: int = MAX_ROWS,
        name: BlockId | None = None,
        label: str | None = None,
    ) -> None:
        super().__init__(name=name, label=label)
        df = to_pandas(df, block="DataTable")

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
