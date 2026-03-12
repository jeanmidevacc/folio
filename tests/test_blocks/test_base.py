"""Tests for BaseBlock, ContainerBlock, and wrap_block."""
from __future__ import annotations

import pytest
import pandas as pd

from folio._error import FolioError
from folio.blocks.base import BaseBlock, ContainerBlock, wrap_block
from folio.blocks.text import Text
from folio.blocks.asset import DataTable


# ── BaseBlock ─────────────────────────────────────────────────────────────────


class TestBaseBlock:
    def test_default_name_and_label_are_none(self):
        b = Text("hello")
        assert b.name is None
        assert b.label is None

    def test_valid_name_accepted(self):
        b = Text("hello", name="my_block")
        assert b.name == "my_block"

    def test_valid_name_with_dashes(self):
        b = Text("hello", name="my-block-1")
        assert b.name == "my-block-1"

    @pytest.mark.parametrize(
        "bad_name",
        [
            "123invalid",   # starts with digit
            "-invalid",     # starts with dash
            "_invalid",     # starts with underscore
            "has space",    # contains space
            "has.dot",      # contains dot
            "",             # empty string
        ],
    )
    def test_invalid_name_raises(self, bad_name):
        with pytest.raises(FolioError, match="Invalid block name"):
            Text("hello", name=bad_name)

    def test_label_stored_as_is_when_short(self):
        b = Text("hi", label="short label")
        assert b.label == "short label"

    def test_label_truncated_at_256_chars(self):
        long_label = "x" * 300
        b = Text("hi", label=long_label)
        assert b.label is not None
        assert len(b.label) <= 256
        assert b.label.endswith("...")

    def test_label_at_exactly_256_chars_not_truncated(self):
        edge_label = "x" * 256
        b = Text("hi", label=edge_label)
        assert b.label == edge_label
        assert not b.label.endswith("...")

    def test_repr_contains_class_name(self):
        b = Text("hello", name="block1")
        assert "Text" in repr(b)
        assert "block1" in repr(b)


# ── ContainerBlock ────────────────────────────────────────────────────────────


class ConcreteContainer(ContainerBlock):
    """Minimal concrete subclass for testing ContainerBlock directly."""


class TestContainerBlock:
    def test_accepts_positional_args(self):
        a, b = Text("a"), Text("b")
        c = ConcreteContainer(a, b)
        assert len(c) == 2
        assert c.blocks[0] is a
        assert c.blocks[1] is b

    def test_accepts_blocks_kwarg(self):
        a, b = Text("a"), Text("b")
        c = ConcreteContainer(blocks=[a, b])
        assert len(c) == 2

    def test_positional_and_kwarg_are_exclusive(self):
        # blocks kwarg takes priority; positional args ignored when blocks= given
        a, b, extra = Text("a"), Text("b"), Text("extra")
        c = ConcreteContainer(extra, blocks=[a, b])
        assert len(c) == 2
        assert c.blocks[0] is a

    def test_empty_container_allowed(self):
        c = ConcreteContainer()
        assert len(c) == 0

    def test_iteration(self):
        a, b = Text("a"), Text("b")
        c = ConcreteContainer(a, b)
        assert list(c) == [a, b]

    def test_repr_shows_block_count(self):
        c = ConcreteContainer(Text("a"), Text("b"))
        assert "2 block(s)" in repr(c)


# ── wrap_block ────────────────────────────────────────────────────────────────


class TestWrapBlock:
    def test_block_passthrough(self):
        t = Text("hello")
        assert wrap_block(t) is t

    def test_str_wraps_to_text(self):
        result = wrap_block("# Hello")
        assert isinstance(result, Text)
        assert result.content == "# Hello"

    def test_dataframe_wraps_to_datatable(self):
        df = pd.DataFrame({"a": [1, 2, 3]})
        result = wrap_block(df)
        assert isinstance(result, DataTable)

    def test_unsupported_type_raises(self):
        with pytest.raises(FolioError, match="Cannot auto-wrap"):
            wrap_block(42)

    def test_unsupported_type_includes_type_name(self):
        with pytest.raises(FolioError, match="int"):
            wrap_block(42)
