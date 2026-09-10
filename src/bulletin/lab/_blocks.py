"""``bulletin.lab`` blocks: DataProfile, DataDive.

DataProfile  — per-column statistics with inline SVG mini-charts.
DataDive     — interactive dot explorer drawn with hand-rolled SVG + vanilla JS.

These live in ``bulletin.lab`` (``pip install bulletin[lab]``) to keep the core
grammar small. The classes here define the public API surface; rendering logic
lives in ``bulletin/lab/_render_profile.py`` and ``bulletin/lab/_render_datadive.py``.
"""
from __future__ import annotations

import typing as t
import warnings

from bulletin._error import BulletinError
from bulletin._frames import to_pandas
from bulletin.blocks.base import Block, BlockId

if t.TYPE_CHECKING:
    import pandas as pd


class DataProfile(Block):
    """Per-column statistical profiling block.

    For each column in the DataFrame, renders:
    - dtype, row count, missing % (highlighted in red when > 20 %)
    - **Numeric columns**: mean, std, min / quartiles / max + inline SVG histogram
    - **Categorical columns**: n_unique, top values + inline SVG bar chart
    - **Datetime columns**: range, gap detection

    Mini-charts are pure SVG — no plotting dependency.

    Example::

        bn.lab.DataProfile(df)
        bn.lab.DataProfile(df, missing_threshold=0.10)  # red at >10% missing
    """

    def __init__(
        self,
        df: pd.DataFrame | t.Any,
        missing_threshold: float = 0.20,
        max_categories: int = 20,
        name: BlockId | None = None,
        label: str | None = None,
    ) -> None:
        if not 0.0 <= missing_threshold <= 1.0:
            raise BulletinError("'missing_threshold' must be between 0.0 and 1.0.")
        super().__init__(name=name, label=label)
        self.df = to_pandas(df, block="DataProfile")
        self.missing_threshold = missing_threshold
        self.max_categories = max_categories


class DataDive(Block):
    """Interactive dot explorer — similar to Google's Facets Dive.

    Each row in the DataFrame becomes a dot in a 2-D space. Dropdowns let the
    viewer dynamically reassign which columns drive X position, Y position,
    colour and facet rows/columns.

    Fully self-contained: the plot is drawn with hand-rolled SVG and vanilla JS
    (no Vega, D3, or CDN). The row data is embedded in the page as JSON.

    Example::

        bn.lab.DataDive(df)
        bn.lab.DataDive(df, x="revenue", y="units", color="region", max_rows=5_000)
    """

    #: DataFrames larger than this are sampled with a warning.
    MAX_ROWS: t.ClassVar[int] = 10_000

    def __init__(
        self,
        df: pd.DataFrame | t.Any,
        x: str | None = None,
        y: str | None = None,
        color: str | None = None,
        facet_row: str | None = None,
        facet_col: str | None = None,
        layout: str = "scatter",
        max_rows: int = MAX_ROWS,
        name: BlockId | None = None,
        label: str | None = None,
    ) -> None:
        if layout not in ("scatter", "tile"):
            raise BulletinError(f"DataDive: 'layout' must be 'scatter' or 'tile', got {layout!r}.")

        super().__init__(name=name, label=label)
        df = to_pandas(df, block="DataDive")

        if len(df) > max_rows:
            warnings.warn(
                f"DataDive: DataFrame has {len(df):,} rows — sampling to {max_rows:,}. "
                "Increase 'max_rows' to include more points.",
                stacklevel=2,
            )
            df = df.sample(max_rows, random_state=42)

        # Validate that explicitly requested columns exist.
        for col_name, col_val in [
            ("x", x), ("y", y), ("color", color),
            ("facet_row", facet_row), ("facet_col", facet_col),
        ]:
            if col_val is not None and col_val not in df.columns:
                raise BulletinError(
                    f"DataDive: column {col_val!r} (passed as '{col_name}') "
                    f"not found in DataFrame. Available: {list(df.columns)}"
                )

        self.df = df
        self.x = x
        self.y = y
        self.color = color
        self.facet_row = facet_row
        self.facet_col = facet_col
        self.layout = layout
        self.max_rows = max_rows


# ── public re-exports ─────────────────────────────────────────────────────────

__all__: list[str] = ["DataDive", "DataProfile"]
