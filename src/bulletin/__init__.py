"""bulletin — build beautiful, self-contained HTML reports from Python analysis.

Quick start::

    import bulletin as bn

    report = bn.Bulletin(
        bn.Text("# My Analysis"),
        bn.Group(
            bn.BigNumber("Accuracy", "92.4%", change="+1.2%", is_upward_change=True),
            bn.BigNumber("F1 Score", 0.89),
            columns=2,
        ),
        bn.Select(
            bn.Plot(fig, label="Chart"),
            bn.DataTable(df, label="Data"),
        ),
    )

    bn.save(report, "analysis.html")
"""
import typing as t
import warnings
import webbrowser
from pathlib import Path

from bulletin._error import BulletinError

# ── blocks ────────────────────────────────────────────────────────────────────
from bulletin.blocks import (
    Alert,
    AlertLevel,
    Block,
    BigNumber,
    Bulletin,
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
from bulletin.renderers.formatting import Formatting, TextAlignment, Width

# ── renderer ──────────────────────────────────────────────────────────────────
from bulletin.renderers.html import render_report


# ── public API ────────────────────────────────────────────────────────────────


def save(
    blocks: Bulletin | list | object,
    path: str,
    *,
    open: bool = False,  # noqa: A002
    name: str = "Report",
    formatting: Formatting | None = None,
) -> None:
    """Save *blocks* as a self-contained HTML file at *path*.

    Args:
        blocks: A :class:`~bulletin.Bulletin` instance, a list of blocks, or a
            single block.  Lists and single blocks are automatically wrapped.
        path: Destination file path (e.g. ``"report.html"``).
        open: Open the file in your default browser after saving.
        name: Document title shown in the browser tab and report header.
        formatting: A :class:`~bulletin.Formatting` instance controlling the theme.

    Example::

        bn.save(report, "analysis.html", name="Q1 Analysis", open=True)
    """
    wrapped = Bulletin.wrap(blocks)  # type: ignore[arg-type]
    html = render_report(wrapped, name=name, formatting=formatting)
    dest = Path(path)
    dest.write_text(html, encoding="utf-8")
    if open:
        webbrowser.open(dest.resolve().as_uri())


def stringify(
    blocks: Bulletin | list | object,
    *,
    name: str = "Report",
    formatting: Formatting | None = None,
) -> str:
    """Render *blocks* to a self-contained HTML string.

    Useful for inline display in Jupyter notebooks::

        from IPython.display import HTML, display
        display(HTML(bn.stringify(report)))
    """
    wrapped = Bulletin.wrap(blocks)  # type: ignore[arg-type]
    return render_report(wrapped, name=name, formatting=formatting)


__version__ = "0.1.0"

__all__: list[str] = [
    # error
    "BulletinError",
    # blocks — text
    "Alert",
    "AlertLevel",
    "BigNumber",
    "Code",
    "Formula",
    "HTML",
    "Text",
    # blocks — layout
    "Block",
    "Bulletin",
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
    "save",
    "stringify",
    # meta
    "__version__",
]


# ── deprecated aliases (removed after 0.2) ───────────────────────────────────

#: old name -> (new name, object)
_RENAMED: dict[str, tuple[str, object]] = {
    "Blocks": ("Bulletin", Bulletin),
    "BaseBlock": ("Block", Block),
    "save_report": ("save", save),
    "stringify_report": ("stringify", stringify),
}


def __getattr__(name: str) -> t.Any:
    if name in _RENAMED:
        new, obj = _RENAMED[name]
        warnings.warn(
            f"bulletin.{name} is deprecated and will be removed after 0.2 — "
            f"use bulletin.{new}.",
            DeprecationWarning,
            stacklevel=2,
        )
        return obj
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
