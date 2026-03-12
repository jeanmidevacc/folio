"""Tests for the pre-render normalization pass."""
from __future__ import annotations

import pytest

from folio._error import FolioError
from folio.blocks.layout import Blocks, Group, Page, Select, SelectType
from folio.blocks.text import Text
from folio.renderers.normalize import normalize


class TestNormalize:
    def test_passthrough_non_page_blocks(self):
        root = Blocks(Text("a"), Text("b"))
        result = normalize(root)
        assert len(result.blocks) == 2
        assert all(isinstance(b, Text) for b in result.blocks)

    def test_empty_blocks_raises(self):
        with pytest.raises(FolioError, match="empty"):
            normalize(Blocks())

    def test_pages_converted_to_select(self):
        root = Blocks(
            Page(Text("content 1"), title="One"),
            Page(Text("content 2"), title="Two"),
        )
        result = normalize(root)
        assert len(result.blocks) == 1
        select = result.blocks[0]
        assert isinstance(select, Select)
        assert select.type == SelectType.TABS

    def test_pages_become_groups_inside_select(self):
        root = Blocks(
            Page(Text("a"), Text("b"), title="Page A"),
            Page(Text("c"), title="Page B"),
        )
        result = normalize(root)
        select = result.blocks[0]
        assert len(select.blocks) == 2
        assert all(isinstance(b, Group) for b in select.blocks)

    def test_page_title_becomes_group_label(self):
        root = Blocks(
            Page(Text("x"), title="Overview"),
            Page(Text("y"), title="Detail"),
        )
        result = normalize(root)
        select = result.blocks[0]
        assert select.blocks[0].label == "Overview"
        assert select.blocks[1].label == "Detail"

    def test_page_name_preserved_on_group(self):
        root = Blocks(
            Page(Text("x"), title="A", name="page-a"),
            Page(Text("y"), title="B", name="page-b"),
        )
        result = normalize(root)
        select = result.blocks[0]
        assert select.blocks[0].name == "page-a"

    def test_mixed_pages_and_blocks_raises(self):
        with pytest.raises(FolioError, match="mix"):
            normalize(Blocks(Page(Text("x"), title="P"), Text("not a page")))

    def test_normalize_does_not_mutate_original(self):
        root = Blocks(Text("a"), Text("b"))
        original_id = id(root.blocks)
        normalize(root)
        assert id(root.blocks) == original_id
