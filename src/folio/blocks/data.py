"""Data analysis blocks: DataProfile, DataDive.

DataProfile  — per-column statistics with inline SVG mini-charts (Phase 5).
DataDive     — Vega-Lite powered interactive dot explorer (Phase 6).

The classes here define the public API surface. Full rendering logic lives in
the renderer (folio/renderers/html.py) and will be fleshed out in later phases.
"""
from __future__ import annotations

import typing as t

from folio._error import FolioError
from folio.blocks.base import BaseBlock, BlockId

if t.TYPE_CHECKING:
    import pandas as pd


def _require_pandas(block_name: str) -> None:
    try:
        import pandas  # noqa: F401
    except ImportError as exc:
        raise FolioError(
            f"{block_name} requires pandas — install it with: pip install pandas"
        ) from exc


class DataProfile(BaseBlock):
    """Per-column statistical profiling block.

    For each column in the DataFrame, renders:
    - dtype, row count, missing % (highlighted in red when > 20 %)
    - **Numeric columns**: mean, std, min / quartiles / max + inline SVG histogram
    - **Categorical columns**: n_unique, top values + inline SVG bar chart
    - **Datetime columns**: range, gap detection

    No extra dependencies beyond pandas — mini-charts are pure SVG.

    Example::

        fl.DataProfile(df)
        fl.DataProfile(df, missing_threshold=0.10)  # red at >10% missing
    """

    def __init__(
        self,
        df: pd.DataFrame,
        missing_threshold: float = 0.20,
        max_categories: int = 20,
        name: BlockId | None = None,
        label: str | None = None,
    ) -> None:
        _require_pandas("DataProfile")
        if not 0.0 <= missing_threshold <= 1.0:
            raise FolioError("'missing_threshold' must be between 0.0 and 1.0.")
        super().__init__(name=name, label=label)
        self.df = df
        self.missing_threshold = missing_threshold
        self.max_categories = max_categories


class DataDive(BaseBlock):
    """Interactive Vega-Lite powered dot explorer.

    Each row in the DataFrame becomes a dot in a 2-D space. Dropdowns let the
    viewer dynamically reassign which columns drive X position, Y position,
    colour and facet rows/columns — similar to Google's Facets Dive.

    Requires Vega + Vega-Lite JS (inlined in the report, ~1 MB).

    Example::

        fl.DataDive(df)
        fl.DataDive(df, x="revenue", y="units", color="region", max_rows=5_000)
    """

    #: DataFrames larger than this are sampled with a warning.
    MAX_ROWS: t.ClassVar[int] = 10_000

    def __init__(
        self,
        df: pd.DataFrame,
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
        _require_pandas("DataDive")
        import warnings

        if layout not in ("scatter", "tile"):
            raise FolioError(f"DataDive: 'layout' must be 'scatter' or 'tile', got {layout!r}.")

        super().__init__(name=name, label=label)

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
                raise FolioError(
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
