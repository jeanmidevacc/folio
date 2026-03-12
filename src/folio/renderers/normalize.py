"""Pre-render normalization pass.

Transforms the block tree before HTML rendering:
- Converts top-level ``Page`` blocks into a ``Select(TABS)`` of ``Group`` blocks.
- Validates that the root ``Blocks`` container is not empty.
"""
from __future__ import annotations

import copy

from folio._error import FolioError
from folio.blocks.layout import Blocks, Group, Page, Select, SelectType


def normalize(blocks: Blocks) -> Blocks:
    """Return a normalized copy of *blocks*, ready for rendering.

    Mutations applied (in order):

    1. **Empty root check** — raises :class:`~folio.FolioError` if the root
       ``Blocks`` has zero children.
    2. **Page → Select conversion** — if *all* top-level children are
       :class:`~folio.Page` blocks they are converted to a single
       ``Select(type=TABS)`` whose children are labelled ``Group`` blocks,
       one per page.  Mixed roots (some Pages, some non-Pages) raise an error.
    """
    root = copy.copy(blocks)
    root.blocks = list(blocks.blocks)  # shallow-copy the list

    if len(root.blocks) == 0:
        raise FolioError(
            "Cannot render an empty Blocks container — add at least one block."
        )

    has_pages = [isinstance(b, Page) for b in root.blocks]

    if any(has_pages) and not all(has_pages):
        raise FolioError(
            "Cannot mix Page blocks with other block types at the top level. "
            "Either wrap all content in Page blocks, or use none."
        )

    if all(has_pages):
        root.blocks = [
            Select(
                blocks=[
                    Group(blocks=page.blocks, label=page.title, name=page.name)
                    for page in root.blocks  # type: ignore[union-attr]
                ],
                type=SelectType.TABS,
            )
        ]

    return root
