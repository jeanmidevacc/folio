"""Core block primitives: BaseBlock, ContainerBlock, and wrap_block."""
from __future__ import annotations

import re
import typing as t

from folio._error import FolioError

_NAME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]*$")
_MAX_LABEL_LEN = 256
_MAX_CAPTION_LEN = 512

BlockId = str
BlockOrPrimitive = t.Union["BaseBlock", t.Any]


class BaseBlock:
    """Base class for all folio blocks.

    All blocks carry an optional ``name`` (a stable ID for referencing the
    block) and an optional ``label`` (a human-readable display string used
    e.g. as a tab title inside a Select).
    """

    def __init__(
        self,
        name: BlockId | None = None,
        label: str | None = None,
    ) -> None:
        if name is not None and not _NAME_RE.match(name):
            raise FolioError(
                f"Invalid block name {name!r}: must start with a letter and contain "
                "only letters, digits, underscores, or hyphens."
            )
        self.name = name
        self.label = _truncate(label, _MAX_LABEL_LEN) if label else label

    def __repr__(self) -> str:
        parts = []
        if self.name:
            parts.append(f"name={self.name!r}")
        if self.label:
            parts.append(f"label={self.label!r}")
        return f"{self.__class__.__name__}({', '.join(parts)})"


class ContainerBlock(BaseBlock):
    """Block that holds a list of child blocks (forms a subtree)."""

    #: Subclasses can raise the bar; checked during rendering, not construction.
    min_blocks: t.ClassVar[int] = 1

    def __init__(
        self,
        *arg_blocks: BlockOrPrimitive,
        blocks: list[BlockOrPrimitive] | None = None,
        name: BlockId | None = None,
        label: str | None = None,
    ) -> None:
        super().__init__(name=name, label=label)
        resolved = list(blocks if blocks is not None else arg_blocks)
        self.blocks: list[BaseBlock] = [wrap_block(b) for b in resolved]

    def __iter__(self) -> t.Iterator[BaseBlock]:
        return iter(self.blocks)

    def __len__(self) -> int:
        return len(self.blocks)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"{len(self.blocks)} block(s)"
            + (f", name={self.name!r}" if self.name else "")
            + ")"
        )


def wrap_block(b: BlockOrPrimitive) -> BaseBlock:
    """Auto-wrap primitives into appropriate blocks.

    Supported auto-wrapping:
    - ``str``          → :class:`~folio.blocks.text.Text`
    - ``pd.DataFrame`` → :class:`~folio.blocks.asset.DataTable`  (Phase 4)
    - plot objects     → :class:`~folio.blocks.asset.Plot`        (Phase 3)
    """
    if isinstance(b, BaseBlock):
        return b

    if isinstance(b, str):
        from folio.blocks.text import Text

        return Text(text=b)

    # Phase 3+: pandas DataFrame and plot objects
    try:
        import pandas as pd

        if isinstance(b, pd.DataFrame):
            from folio.blocks.asset import DataTable

            return DataTable(b)
    except ImportError:
        pass

    raise FolioError(
        f"Cannot auto-wrap {type(b).__name__!r} into a folio block. "
        "Pass a folio block, a string, or a pandas DataFrame."
    )


# ── helpers ──────────────────────────────────────────────────────────────────


def _truncate(s: str, max_len: int) -> str:
    return s[: max_len - 3] + "..." if len(s) > max_len else s
