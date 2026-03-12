"""Tests for the HTML renderer.

All structural assertions parse the rendered HTML with BeautifulSoup so we
make real DOM-level checks rather than brittle string matching.
"""
from __future__ import annotations

import re

import pytest
from bs4 import BeautifulSoup

import folio as fl
from folio.blocks.layout import Blocks, Group, Select, SelectType, Toggle
from folio.blocks.text import Alert, AlertLevel, BigNumber, Code, Formula, HTML, Text
from folio.renderers.formatting import Formatting, Width
from folio.renderers.html import render_report


# ── helpers ───────────────────────────────────────────────────────────────────


def parse(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


def render(blocks: Blocks, **kwargs) -> BeautifulSoup:
    return parse(render_report(blocks, **kwargs))


def blocks(*args) -> Blocks:
    return Blocks(*args)


# ── self-contained guarantee ──────────────────────────────────────────────────


class TestSelfContained:
    def test_no_external_script_src(self):
        soup = render(blocks(Text("hi")))
        for tag in soup.find_all("script", src=True):
            assert not tag["src"].startswith("http"), f"External script: {tag['src']}"

    def test_no_external_link_href(self):
        soup = render(blocks(Text("hi")))
        for tag in soup.find_all("link", href=True):
            assert not tag["href"].startswith("http"), f"External link: {tag['href']}"

    def test_no_external_img_src(self):
        soup = render(blocks(Text("hi")))
        for tag in soup.find_all("img", src=True):
            assert not tag["src"].startswith("http"), f"External image: {tag['src']}"

    def test_output_is_parseable_html(self):
        soup = render(blocks(Text("# Hello")))
        assert soup.find("html") is not None
        assert soup.find("body") is not None


# ── document structure ────────────────────────────────────────────────────────


class TestDocumentStructure:
    def test_title_in_head(self):
        soup = render(blocks(Text("hi")), name="My Report")
        assert soup.find("title").text == "My Report"

    def test_header_shown_when_name_not_default(self):
        soup = render(blocks(Text("hi")), name="Sales Q1")
        assert soup.find(class_="fl-report__header") is not None

    def test_header_hidden_when_default_name(self):
        soup = render(blocks(Text("hi")), name="Report")
        assert soup.find(class_="fl-report__header") is None

    def test_report_date_present_in_header(self):
        soup = render(blocks(Text("hi")), name="X")
        assert soup.find("time") is not None

    def test_css_in_style_tag(self):
        soup = render(blocks(Text("hi")))
        styles = soup.find_all("style")
        assert any("fl-report" in s.text for s in styles)

    def test_js_in_script_tag(self):
        soup = render(blocks(Text("hi")))
        scripts = [s for s in soup.find_all("script") if not s.get("src")]
        assert any("fl-select" in s.text for s in scripts)

    def test_formatting_css_vars_injected(self):
        fmt = Formatting(accent_color="#ff0000")
        soup = render(blocks(Text("hi")), formatting=fmt)
        style_text = " ".join(s.text for s in soup.find_all("style"))
        assert "#ff0000" in style_text


# ── Text block ────────────────────────────────────────────────────────────────


class TestTextRendering:
    def test_markdown_h1_rendered(self):
        soup = render(blocks(Text("# Hello World")))
        assert soup.find("h1") is not None
        assert "Hello World" in soup.find("h1").text

    def test_markdown_bold(self):
        soup = render(blocks(Text("**bold text**")))
        assert soup.find("strong") is not None

    def test_markdown_link(self):
        soup = render(blocks(Text("[click me](https://example.com)")))
        link = soup.find("a")
        assert link is not None

    def test_wrapped_in_fl_text(self):
        soup = render(blocks(Text("hello")))
        assert soup.find(class_="fl-text") is not None


# ── HTML block ────────────────────────────────────────────────────────────────


class TestHTMLRendering:
    def test_raw_html_preserved(self):
        soup = render(blocks(HTML("<b>bold</b>")))
        assert soup.find("b") is not None
        assert soup.find("b").text == "bold"

    def test_wrapped_in_fl_html(self):
        soup = render(blocks(HTML("<span>x</span>")))
        assert soup.find(class_="fl-html") is not None


# ── Code block ────────────────────────────────────────────────────────────────


class TestCodeRendering:
    def test_pre_code_present(self):
        soup = render(blocks(Code("x = 1")))
        assert soup.find("pre") is not None
        assert soup.find("code") is not None

    def test_language_in_class(self):
        soup = render(blocks(Code("SELECT 1", language="sql")))
        code = soup.find("code")
        assert "language-sql" in code.get("class", [])

    def test_caption_rendered(self):
        soup = render(blocks(Code("x", caption="My snippet")))
        assert "My snippet" in soup.get_text()

    def test_no_caption_when_none(self):
        soup = render(blocks(Code("x")))
        assert soup.find(class_="fl-code__caption") is None


# ── BigNumber block ───────────────────────────────────────────────────────────


class TestBigNumberRendering:
    def test_value_present(self):
        soup = render(blocks(BigNumber("Revenue", "$4.2M")))
        assert "$4.2M" in soup.get_text()

    def test_heading_present(self):
        soup = render(blocks(BigNumber("Revenue", "$4.2M")))
        assert "Revenue" in soup.get_text()

    def test_upward_change_class(self):
        soup = render(blocks(BigNumber("x", 1, change="+5%", is_upward_change=True)))
        assert soup.find(class_="fl-bignumber__change--up") is not None

    def test_downward_change_class(self):
        soup = render(blocks(BigNumber("x", 1, change="-5%", is_upward_change=False)))
        assert soup.find(class_="fl-bignumber__change--down") is not None

    def test_no_change_element_when_absent(self):
        soup = render(blocks(BigNumber("x", 1)))
        assert soup.find(class_="fl-bignumber__change") is None


# ── Alert block ───────────────────────────────────────────────────────────────


class TestAlertRendering:
    @pytest.mark.parametrize("level", list(AlertLevel))
    def test_level_class_present(self, level: AlertLevel):
        soup = render(blocks(Alert("msg", level=level)))
        assert soup.find(class_=f"fl-alert--{level.value}") is not None

    def test_message_rendered(self):
        soup = render(blocks(Alert("Something went wrong.")))
        assert "Something went wrong." in soup.get_text()

    def test_title_rendered_when_set(self):
        soup = render(blocks(Alert("msg", title="Heads up")))
        assert "Heads up" in soup.get_text()
        assert soup.find(class_="fl-alert__title") is not None

    def test_no_title_element_when_absent(self):
        soup = render(blocks(Alert("msg")))
        assert soup.find(class_="fl-alert__title") is None


# ── Group block ───────────────────────────────────────────────────────────────


class TestGroupRendering:
    def test_fl_group_present(self):
        soup = render(blocks(Group(Text("a"), Text("b"), columns=2)))
        assert soup.find(class_="fl-group") is not None

    def test_column_count_in_style(self):
        soup = render(blocks(Group(Text("a"), Text("b"), columns=2)))
        group = soup.find(class_="fl-group")
        assert "--fl-cols: 2" in group.get("style", "")

    def test_custom_widths_in_style(self):
        soup = render(blocks(Group(Text("a"), Text("b"), columns=2, widths=[3, 1])))
        group = soup.find(class_="fl-group")
        assert "3fr" in group.get("style", "")
        assert "1fr" in group.get("style", "")

    def test_children_rendered(self):
        soup = render(blocks(Group(Text("**hello**"), Text("world"), columns=2)))
        assert soup.find("strong") is not None


# ── Select block ──────────────────────────────────────────────────────────────


class TestSelectRendering:
    def test_tab_buttons_rendered(self):
        s = Select(Text("a", label="Tab A"), Text("b", label="Tab B"))
        soup = render(blocks(s))
        tabs = soup.find_all(class_="fl-select__tab")
        assert len(tabs) == 2

    def test_tab_labels_used(self):
        s = Select(Text("a", label="First"), Text("b", label="Second"))
        soup = render(blocks(s))
        text = soup.get_text()
        assert "First" in text
        assert "Second" in text

    def test_panels_rendered(self):
        s = Select(Text("content A", label="A"), Text("content B", label="B"))
        soup = render(blocks(s))
        panels = soup.find_all(class_="fl-select__panel")
        assert len(panels) == 2

    def test_dropdown_select_element_present(self):
        s = Select(
            Text("a", label="A"), Text("b", label="B"), type=SelectType.DROPDOWN
        )
        soup = render(blocks(s))
        assert soup.find("select") is not None

    def test_fallback_tab_label(self):
        # No label set on children → should fall back to "Tab N"
        s = Select(Text("a"), Text("b"))
        soup = render(blocks(s))
        assert "Tab 1" in soup.get_text()


# ── Toggle block ──────────────────────────────────────────────────────────────


class TestToggleRendering:
    def test_toggle_header_present(self):
        soup = render(blocks(Toggle(Text("details"), label="Show more")))
        assert soup.find(class_="fl-toggle__header") is not None

    def test_label_in_header(self):
        soup = render(blocks(Toggle(Text("x"), label="Click me")))
        assert "Click me" in soup.get_text()

    def test_body_present(self):
        soup = render(blocks(Toggle(Text("inner content"), label="Toggle")))
        assert soup.find(class_="fl-toggle__body") is not None

    def test_aria_expanded_false_by_default(self):
        soup = render(blocks(Toggle(Text("x"), label="T")))
        header = soup.find(class_="fl-toggle__header")
        assert header.get("aria-expanded") == "false"


# ── public API ────────────────────────────────────────────────────────────────


class TestPublicAPI:
    def test_save_report_writes_file(self, tmp_path):
        report = fl.Blocks(fl.Text("# Hello"))
        dest = tmp_path / "out.html"
        fl.save_report(report, str(dest), name="Test")
        assert dest.exists()
        assert dest.stat().st_size > 0
        content = dest.read_text(encoding="utf-8")
        assert "<!DOCTYPE html>" in content

    def test_save_report_self_contained(self, tmp_path):
        report = fl.Blocks(fl.Text("hi"))
        dest = tmp_path / "out.html"
        fl.save_report(report, str(dest))
        soup = parse(dest.read_text(encoding="utf-8"))
        for tag in soup.find_all(src=True):
            assert not str(tag.get("src", "")).startswith("http")

    def test_stringify_report_returns_string(self):
        report = fl.Blocks(fl.Text("hello"))
        result = fl.stringify_report(report)
        assert isinstance(result, str)
        assert "<!DOCTYPE html>" in result

    def test_save_report_accepts_list(self, tmp_path):
        dest = tmp_path / "out.html"
        fl.save_report([fl.Text("a"), fl.Text("b")], str(dest))
        assert dest.exists()

    def test_save_report_accepts_single_block(self, tmp_path):
        dest = tmp_path / "out.html"
        fl.save_report(fl.Text("solo"), str(dest))
        assert dest.exists()

    def test_formatting_applied(self, tmp_path):
        dest = tmp_path / "out.html"
        fl.save_report(
            fl.Blocks(fl.Text("hi")),
            str(dest),
            formatting=fl.Formatting(accent_color="#cafe00"),
        )
        assert "#cafe00" in dest.read_text(encoding="utf-8")

    def test_width_narrow_in_css(self, tmp_path):
        dest = tmp_path / "out.html"
        fl.save_report(
            fl.Blocks(fl.Text("hi")),
            str(dest),
            formatting=fl.Formatting(width=Width.NARROW),
        )
        assert "48rem" in dest.read_text(encoding="utf-8")
