"""Tests for layout blocks: Group, Select, Toggle, Page, Blocks."""
from __future__ import annotations

import warnings

import pytest

from folio._error import FolioError
from folio.blocks.layout import Blocks, Group, Page, Select, SelectType, Toggle, VAlign
from folio.blocks.text import Text


# ── helpers ───────────────────────────────────────────────────────────────────


def make_texts(n: int) -> list[Text]:
    return [Text(f"Block {i}", label=f"Tab {i}") for i in range(n)]


# ── Group ─────────────────────────────────────────────────────────────────────


class TestGroup:
    def test_single_column_default(self):
        g = Group(*make_texts(2))
        assert g.columns == 1

    def test_multi_column(self):
        g = Group(*make_texts(3), columns=3)
        assert g.columns == 3
        assert len(g) == 3

    def test_blocks_kwarg(self):
        items = make_texts(2)
        g = Group(blocks=items, columns=2)
        assert len(g) == 2

    def test_widths_correct_length(self):
        g = Group(*make_texts(2), columns=2, widths=[2, 1])
        assert g.widths == [2, 1]

    def test_widths_wrong_length_raises(self):
        with pytest.raises(FolioError, match="widths"):
            Group(*make_texts(2), columns=2, widths=[1, 2, 3])

    def test_valign_default(self):
        g = Group(*make_texts(2))
        assert g.valign == VAlign.TOP

    def test_valign_set(self):
        g = Group(*make_texts(2), valign=VAlign.CENTER)
        assert g.valign == VAlign.CENTER

    def test_valign_string_coerced(self):
        g = Group(*make_texts(2), valign="bottom")
        assert g.valign == VAlign.BOTTOM

    def test_empty_group_allowed(self):
        g = Group()
        assert len(g) == 0

    def test_string_auto_wrapped(self):
        g = Group("# Title", Text("body"), columns=2)
        assert len(g) == 2
        # The string should be wrapped into a Text block
        from folio.blocks.text import Text as T
        assert isinstance(g.blocks[0], T)

    def test_name_and_label(self):
        g = Group(*make_texts(2), name="grid-1", label="Grid")
        assert g.name == "grid-1"
        assert g.label == "Grid"


# ── Select ────────────────────────────────────────────────────────────────────


class TestSelect:
    def test_default_type_is_tabs(self):
        s = Select(*make_texts(2))
        assert s.type == SelectType.TABS

    def test_dropdown_type(self):
        s = Select(*make_texts(2), type=SelectType.DROPDOWN)
        assert s.type == SelectType.DROPDOWN

    def test_string_type_coerced(self):
        s = Select(*make_texts(2), type="dropdown")
        assert s.type == SelectType.DROPDOWN

    def test_fewer_than_2_blocks_warns(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            Select(Text("only one"))
        assert any("at least 2" in str(w.message) for w in caught)

    def test_exactly_2_blocks_no_warning(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            Select(*make_texts(2))
        assert not any("at least 2" in str(w.message) for w in caught)

    def test_many_blocks_accepted(self):
        s = Select(*make_texts(5))
        assert len(s) == 5

    def test_blocks_kwarg(self):
        items = make_texts(3)
        s = Select(blocks=items)
        assert len(s) == 3


# ── Toggle ────────────────────────────────────────────────────────────────────


class TestToggle:
    def test_single_block(self):
        t = Toggle(Text("content"), label="Show details")
        assert len(t) == 1
        assert t.label == "Show details"

    def test_multiple_blocks_wrapped_in_group(self):
        t = Toggle(*make_texts(3))
        # Multiple blocks should be wrapped into a single Group.
        assert len(t) == 1
        assert isinstance(t.blocks[0], Group)

    def test_single_block_not_wrapped(self):
        inner = Text("only one")
        t = Toggle(inner)
        assert t.blocks[0] is inner

    def test_name_stored(self):
        t = Toggle(Text("x"), name="toggle-1")
        assert t.name == "toggle-1"


# ── Page ──────────────────────────────────────────────────────────────────────


class TestPage:
    def test_title_stored_as_label(self):
        p = Page(Text("content"), title="Overview")
        assert p.title == "Overview"
        assert p.label == "Overview"

    def test_no_title_is_none(self):
        p = Page(Text("content"))
        assert p.title is None
        assert p.label is None

    def test_nested_page_raises(self):
        with pytest.raises(FolioError, match="Nested Page"):
            Page(Page(Text("inner")))

    def test_blocks_kwarg(self):
        items = make_texts(2)
        p = Page(blocks=items, title="My Page")
        assert len(p) == 2

    def test_name_stored(self):
        p = Page(Text("x"), name="page-1")
        assert p.name == "page-1"


# ── Blocks ────────────────────────────────────────────────────────────────────


class TestBlocks:
    def test_basic(self):
        b = Blocks(*make_texts(3))
        assert len(b) == 3

    def test_single_blocks_unwrapped(self):
        inner = Blocks(Text("a"), Text("b"))
        outer = Blocks(inner)
        # Passing a single Blocks into Blocks should flatten it.
        assert len(outer) == 2

    def test_string_auto_wrapped(self):
        b = Blocks("# Hello", Text("world"))
        assert len(b) == 2

    def test_wrap_from_blocks_instance(self):
        original = Blocks(*make_texts(2))
        wrapped = Blocks.wrap(original)
        assert wrapped is original

    def test_wrap_from_list(self):
        items = make_texts(3)
        wrapped = Blocks.wrap(items)
        assert isinstance(wrapped, Blocks)
        assert len(wrapped) == 3

    def test_wrap_from_single_block(self):
        t = Text("only")
        wrapped = Blocks.wrap(t)
        assert isinstance(wrapped, Blocks)
        assert len(wrapped) == 1

    def test_blocks_kwarg(self):
        items = make_texts(2)
        b = Blocks(blocks=items)
        assert len(b) == 2

    def test_iteration(self):
        items = make_texts(3)
        b = Blocks(*items)
        assert list(b) == items
