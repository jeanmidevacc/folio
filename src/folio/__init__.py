"""folio — build beautiful, self-contained HTML reports from Python analysis.

Quick start::

    import folio as fl

    report = fl.Blocks(
        fl.Text("# My Analysis"),
        fl.Group(
            fl.BigNumber("Accuracy", "92.4%", change="+1.2%", is_upward_change=True),
            fl.BigNumber("F1 Score", 0.89),
            columns=2,
        ),
        fl.Select(
            fl.Plot(fig, label="Chart"),
            fl.DataTable(df, label="Data"),
        ),
    )

    fl.save_report(report, "analysis.html")
"""
import webbrowser
from pathlib import Path

from folio._error import FolioError

# ── blocks ────────────────────────────────────────────────────────────────────
from folio.blocks import (
    Alert,
    AlertLevel,
    BaseBlock,
    BigNumber,
    Blocks,
    Code,
    DataDive,
    DataProfile,
    DataTable,
    Formula,
    Group,
    HTML,
    Page,
    Plot,
    Select,
    SelectType,
    Table,
    Text,
    Toggle,
    VAlign,
    wrap_block,
)

# ── formatting ────────────────────────────────────────────────────────────────
from folio.renderers.formatting import Formatting, TextAlignment, Width

# ── renderer ──────────────────────────────────────────────────────────────────
from folio.renderers.html import render_report


# ── public API ────────────────────────────────────────────────────────────────


def save_report(
    blocks: Blocks | list | object,
    path: str,
    *,
    open: bool = False,  # noqa: A002
    name: str = "Report",
    formatting: Formatting | None = None,
) -> None:
    """Save *blocks* as a self-contained HTML file at *path*.

    Args:
        blocks: A :class:`~folio.Blocks` instance, a list of blocks, or a
            single block.  Lists and single blocks are automatically wrapped.
        path: Destination file path (e.g. ``"report.html"``).
        open: Open the file in your default browser after saving.
        name: Document title shown in the browser tab and report header.
        formatting: A :class:`~folio.Formatting` instance controlling the theme.

    Example::

        fl.save_report(report, "analysis.html", name="Q1 Analysis", open=True)
    """
    wrapped = Blocks.wrap(blocks)  # type: ignore[arg-type]
    html = render_report(wrapped, name=name, formatting=formatting)
    dest = Path(path)
    dest.write_text(html, encoding="utf-8")
    if open:
        webbrowser.open(dest.resolve().as_uri())


def stringify_report(
    blocks: Blocks | list | object,
    *,
    name: str = "Report",
    formatting: Formatting | None = None,
) -> str:
    """Render *blocks* to a self-contained HTML string.

    Useful for inline display in Jupyter notebooks::

        from IPython.display import HTML, display
        display(HTML(fl.stringify_report(report)))
    """
    wrapped = Blocks.wrap(blocks)  # type: ignore[arg-type]
    return render_report(wrapped, name=name, formatting=formatting)


__version__ = "0.1.0"

__all__: list[str] = [
    # error
    "FolioError",
    # blocks — text
    "Alert",
    "AlertLevel",
    "BigNumber",
    "Code",
    "Formula",
    "HTML",
    "Text",
    # blocks — layout
    "BaseBlock",
    "Blocks",
    "Group",
    "Page",
    "Select",
    "SelectType",
    "Toggle",
    "VAlign",
    "wrap_block",
    # blocks — asset
    "DataTable",
    "Plot",
    "Table",
    # blocks — data
    "DataDive",
    "DataProfile",
    # formatting
    "Formatting",
    "TextAlignment",
    "Width",
    # api
    "save_report",
    "stringify_report",
    # meta
    "__version__",
]
