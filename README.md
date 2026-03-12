# folio

Build beautiful, self-contained HTML reports from Python analysis.

## Why folio exists

Two libraries shaped how I thought about sharing data science work:

- **[datapane](https://github.com/datapane/datapane)** — the cleanest Python-native report builder I had ever used. Block-based, self-contained HTML output, dead-simple API. It was decommissioned in 2023 and the SaaS shut down shortly after.
- **[Facets](https://github.com/PAIR-code/facets)** (PAIR / Google) — specifically *Facets Dive*, a brilliant interactive dot explorer that let you slice any dataset visually with zero configuration. The project went largely unmaintained and quietly disappeared from most data science workflows.

I never found a substitute that matched either of them, let alone both at once. folio is my attempt to fill that gap: a datapane-style block and layout system with a Facets Dive-class explorer built in, fully offline, no cloud account required.

Building folio also serves a second purpose: it is a real-world, non-trivial Python project used to benchmark coding agents such as [Claude Code](https://github.com/anthropics/claude-code). Designing a library from original source code — with concept ofblock hierarchy, rendering pipeline, theming, interactive components — gives a coding agent enough surface area to show where it genuinely helps and where it still struggles.

```python
import folio as fl

report = fl.Blocks(
    fl.Text("# Sales Analysis — Q1 2024"),
    fl.Group(
        fl.BigNumber("Revenue", "$4.2M", change="-12%", is_upward_change=False),
        fl.BigNumber("Active Users", "142K", change="+3%", is_upward_change=True),
        columns=2,
    ),
    fl.Select(
        fl.Plot(fig, label="Trend"),
        fl.DataTable(df, label="Raw Data"),
        fl.DataProfile(df, label="Profile"),
    ),
    fl.DataDive(df),
)

fl.save_report(report, "q1_analysis.html")
```

## Features

- **Self-contained HTML** — zero CDN, works offline forever
- **Library-agnostic charts** — Plotly, Altair, Matplotlib, Bokeh
- **Interactive tables** — sortable, searchable DataTable with client-side pagination
- **Data profiling** — per-column stats with inline SVG mini-charts, no extra deps
- **DataDive** — Facets Dive-style interactive dot explorer (Vega-Lite powered)
- **Themes** — five built-in presets plus full CSS token control
- **Pandas 2.x** first-class support; PySpark via `.toPandas()`

## Installation

```bash
pip install folio
# with email support
pip install folio[email]
```

---

## Quick start

```python
import pandas as pd
import folio as fl

df = pd.read_csv("sales.csv")

fl.save_report(
    fl.Blocks(
        fl.Text("# My Report"),
        fl.DataTable(df),
    ),
    path="report.html",
    open=True,          # opens in browser immediately
)
```

To get an HTML string instead of writing a file (useful in Jupyter):

```python
from IPython.display import HTML, display

display(HTML(fl.stringify_report(fl.Blocks(fl.Text("# Hello")))))
```

---

## API

### `fl.save_report`

```python
fl.save_report(
    blocks,                  # Blocks, list, or a single block
    path,                    # destination file — e.g. "report.html"
    *,
    open=False,              # open in default browser after saving
    name="Report",           # browser tab title and report header
    formatting=None,         # Formatting instance — controls theme
)
```

### `fl.stringify_report`

```python
html: str = fl.stringify_report(
    blocks,
    *,
    name="Report",
    formatting=None,
)
```

---

## Block reference

### Text blocks

#### `fl.Text` — Markdown

```python
fl.Text("# Heading\n\nSome **bold** and *italic* text.")

# From a .md file
fl.Text(file="notes.md")
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `text` | `str` | Markdown string (dedented automatically) |
| `file` | `str \| Path` | Path to a `.md` file (alternative to `text`) |
| `label` | `str` | Tab/selector label when used inside `Select` |

Supports headings, bold, italics, inline code, blockquotes, tables, and lists.

---

#### `fl.Code` — Syntax-highlighted code

```python
fl.Code("SELECT * FROM orders LIMIT 10", language="sql")
fl.Code(
    "import folio as fl\nfl.save_report(fl.Blocks(fl.Text('# Hi')), 'out.html')",
    language="python",
    caption="Minimal report",
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `code` | `str` | — | Source code string |
| `language` | `str` | `"python"` | Syntax highlighting language |
| `caption` | `str` | `None` | Optional caption shown below the block |

---

#### `fl.Formula` — LaTeX equation

```python
fl.Formula(r"\bar{x} = \frac{1}{n}\sum_{i=1}^{n} x_i", caption="Sample mean")
```

Rendered via MathJax (inlined in the report — no CDN needed).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `formula` | `str` | — | LaTeX expression (without `$$` delimiters) |
| `caption` | `str` | `None` | Optional caption |

---

#### `fl.HTML` — Raw HTML fragment

```python
fl.HTML("<p style='color:#4F46E5'>Custom <strong>HTML</strong>.</p>")
```

Rendered inside a sandboxed container — inline styles work, scripts are stripped.

---

#### `fl.BigNumber` — KPI metric

```python
fl.BigNumber("Revenue", "$4.2M", change="-12%", is_upward_change=False)
fl.BigNumber("Accuracy", 0.924)   # no change indicator
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `heading` | `str` | — | Metric label |
| `value` | `str \| int \| float` | — | Headline value |
| `change` | `str` | `None` | Delta string, e.g. `"+3.1%"` |
| `is_upward_change` | `bool` | `None` | `True` = green arrow, `False` = red arrow. Required if `change` is set. |

> If `change` is provided without `is_upward_change` a warning is issued and no arrow is shown.

---

#### `fl.Alert` — Callout box

```python
fl.Alert("Pipeline completed successfully.", level=fl.AlertLevel.SUCCESS)
fl.Alert("Margin erosion in South region.", level="warning", title="Watch")
fl.Alert("Legacy source decommissioned.", level=fl.AlertLevel.ERROR, title="Breaking change")
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `message` | `str` | — | Alert body text |
| `level` | `AlertLevel \| str` | `"info"` | One of `info`, `success`, `warning`, `error` |
| `title` | `str` | `None` | Optional bold title above the message |

`fl.AlertLevel` values: `INFO`, `SUCCESS`, `WARNING`, `ERROR`.

---

### Layout blocks

#### `fl.Group` — Grid layout

Arranges child blocks in a responsive column grid.

```python
fl.Group(plot_a, plot_b, columns=2)
fl.Group(a, b, c, columns=3, widths=[2, 1, 1])   # relative column widths
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `*blocks` | `BaseBlock` | — | Child blocks (positional) |
| `columns` | `int` | `1` | Number of columns |
| `widths` | `list[int \| float]` | `None` | Relative column widths — must match `columns` |
| `valign` | `VAlign \| str` | `"top"` | Vertical alignment: `top`, `center`, `bottom` |
| `label` | `str` | `None` | Tab label when used inside `Select` |

---

#### `fl.Select` — Tabbed or dropdown panel switcher

Shows one child block at a time. Each child's `label` becomes the tab title.

```python
fl.Select(
    fl.Plot(fig, label="Chart"),
    fl.DataTable(df, label="Data"),
    fl.DataProfile(df, label="Profile"),
    type=fl.SelectType.TABS,       # or fl.SelectType.DROPDOWN
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `*blocks` | `BaseBlock` | — | Child blocks — each should have a `label` |
| `type` | `SelectType \| str` | `"tabs"` | `"tabs"` or `"dropdown"` |

> Warns if fewer than 2 children are provided.

---

#### `fl.Toggle` — Collapsible section

Collapsed by default; click the label to expand.

```python
fl.Toggle(
    fl.Text("Methodology notes — hidden by default."),
    fl.Code("SELECT * FROM sales\n", language="sql"),
    label="Query details",
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `*blocks` | `BaseBlock` | — | Content blocks (multiple are auto-wrapped in a `Group`) |
| `label` | `str` | `None` | Clickable toggle label |

---

#### `fl.Page` — Top-level page tab

Use at the root of `Blocks` to create multi-page reports. Pages are converted to a top-level tab bar during rendering.

```python
fl.Blocks(
    fl.Page(summary_group, title="Summary"),
    fl.Page(detail_group, title="Detail"),
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `*blocks` | `BaseBlock` | — | Page content |
| `title` | `str` | `None` | Tab title |

> Nested `Page` blocks are not supported — use `Select` and `Group` instead.

---

#### `fl.Blocks` — Root document container

Top-level wrapper passed to `save_report`. Accepts any combination of blocks.

```python
report = fl.Blocks(
    fl.Text("# My Report"),
    fl.Plot(fig),
    fl.DataTable(df),
)
fl.save_report(report, "report.html")
```

---

### Asset blocks

#### `fl.Plot` — Chart / figure

Library-agnostic chart block. Auto-detects the figure type at render time:

| Library | Output |
|---------|--------|
| **Plotly** | Interactive HTML (inline JS) |
| **Altair / Vega-Lite** | Embedded Vega spec |
| **Matplotlib / Seaborn / Plotnine** | Inline SVG |
| **Bokeh** | Inline resources |

```python
fl.Plot(plotly_fig, caption="Revenue over time")
fl.Plot(altair_chart, label="Chart", responsive=True)
fl.Plot(mpl_fig, scale=1.5)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `figure` | any | — | Figure object from Plotly, Altair, Matplotlib, or Bokeh |
| `caption` | `str` | `None` | Caption shown below the chart |
| `responsive` | `bool` | `True` | Scale chart to fill container width |
| `scale` | `float` | `1.0` | Scale multiplier (Matplotlib/static figures) |

---

#### `fl.Table` — Static table (pandas Styler)

Best for formatted DataFrames where you want to preserve Styler rules.

```python
fl.Table(df)
fl.Table(
    df.style
      .format({"revenue": "€ {:,.0f}"})
      .bar(subset=["revenue"], color="#c7d2fe")
      .set_caption("Top 20 by revenue"),
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `DataFrame \| Styler` | — | DataFrame or styled DataFrame |
| `caption` | `str` | `None` | Optional caption |

---

#### `fl.DataTable` — Interactive table

Sortable, searchable, paginated table. Handles large datasets gracefully.

```python
fl.DataTable(df, caption="Full sales dataset")
fl.DataTable(df, max_rows=500)   # cap at 500 rows
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `df` | `DataFrame` | — | Source data |
| `caption` | `str` | `None` | Optional caption |
| `max_rows` | `int` | `10 000` | Rows beyond this are truncated with a warning |

---

### Data blocks

#### `fl.DataProfile` — Column statistics

Renders one card per column with dtype, missing %, and a mini-chart.

- **Numeric** — mean, std, min/quartiles/max + inline histogram
- **Categorical** — n_unique, top values + inline bar chart
- **Datetime** — date range + gap detection

No extra dependencies — mini-charts are pure SVG.

```python
fl.DataProfile(df)
fl.DataProfile(df, missing_threshold=0.05)   # red highlight at >5% missing
fl.DataProfile(df, max_categories=10)        # cap top-N bars for categoricals
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `df` | `DataFrame` | — | Source data |
| `missing_threshold` | `float` | `0.20` | Missing % above which the cell is highlighted red |
| `max_categories` | `int` | `20` | Max top-value bars for categorical columns |

---

#### `fl.DataDive` — Interactive dot explorer

Each DataFrame row becomes a dot. Dropdowns let the viewer dynamically change which columns drive X, Y, colour, and facets — similar to Google Facets Dive.

```python
fl.DataDive(df)                                              # auto-selects axes
fl.DataDive(df, x="revenue", y="margin_pct", color="region")
fl.DataDive(df, x="region", y="channel", color="product", layout="tile")
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `df` | `DataFrame` | — | Source data |
| `x` | `str` | `None` | Initial X-axis column |
| `y` | `str` | `None` | Initial Y-axis column |
| `color` | `str` | `None` | Initial colour column |
| `facet_row` | `str` | `None` | Column to facet into rows |
| `facet_col` | `str` | `None` | Column to facet into columns |
| `layout` | `str` | `"scatter"` | `"scatter"` (2-D axes) or `"tile"` (packed dot grid) |
| `max_rows` | `int` | `10 000` | Rows beyond this are sampled with a warning |

---

## Theming

Pass a `Formatting` instance to `save_report` to control the visual style.

### Built-in presets

```python
fl.save_report(blocks, "out.html", formatting=fl.Formatting.dark())
fl.save_report(blocks, "out.html", formatting=fl.Formatting.corporate())
fl.save_report(blocks, "out.html", formatting=fl.Formatting.minimal())
fl.save_report(blocks, "out.html", formatting=fl.Formatting.ocean())
fl.save_report(blocks, "out.html", formatting=fl.Formatting.warm())
```

| Preset | Description |
|--------|-------------|
| `dark()` | Slate dark — easy on the eyes, great for dashboards |
| `corporate()` | Clean blue corporate — neutral tones, sharp corners |
| `minimal()` | Ultra-clean — white space, black text, hairline borders |
| `ocean()` | Deep teal — rich mid-dark, emerald accent |
| `warm()` | Cream backgrounds — amber accent, serif font |

### Fine-tuning a preset

Every preset accepts keyword overrides:

```python
formatting=fl.Formatting.dark(accent_color="#f43f5e")   # dark theme, rose accent
formatting=fl.Formatting.corporate(width=fl.Width.FULL) # full-width corporate
```

### Building from scratch

```python
formatting=fl.Formatting(
    accent_color="#0369a1",
    bg_color="#f8fafc",
    surface_color="#e2e8f0",
    border_color="#cbd5e1",
    text_color="#0f172a",
    muted_color="#64748b",
    radius="0.25rem",
    width=fl.Width.NARROW,
)
```

### `Formatting` token reference

| Token | Default | Controls |
|-------|---------|---------|
| `accent_color` | `#4F46E5` | Tab underlines, active borders, links, focus rings |
| `bg_color` | `#ffffff` | Page background |
| `text_color` | `#111827` | Body and heading text |
| `muted_color` | `#6b7280` | Labels, captions, axis text, icons |
| `border_color` | `#e5e7eb` | Table borders, card borders, dividers |
| `surface_color` | `#f9fafb` | Card / table-header / code-block backgrounds |
| `font` | `Inter, ui-sans-serif, …` | CSS font-family stack |
| `radius` | `0.5rem` | Border-radius on cards, badges, buttons |
| `width` | `Width.MEDIUM` | Container max-width (`NARROW` / `MEDIUM` / `FULL` or raw CSS) |
| `text_alignment` | `left` | Paragraph text alignment |

`fl.Width` values: `NARROW` (768 px), `MEDIUM` (1200 px), `FULL` (100%).

---

## Recipes

### KPI dashboard with tabbed detail

```python
import folio as fl

fl.save_report(
    fl.Blocks(
        fl.Text("# Sales Analysis — 2023"),

        fl.Group(
            fl.BigNumber("Total Revenue", "€ 1 260 000", change="+12.4%", is_upward_change=True),
            fl.BigNumber("Units Sold",    "12 640",      change="+3.1%",  is_upward_change=True),
            fl.BigNumber("Avg Margin",    "31.2 %",      change="-0.8%",  is_upward_change=False),
            fl.BigNumber("Return Rate",   "8.0 %",       change="+0.2%",  is_upward_change=False),
            columns=4,
        ),

        fl.Alert("South region margin dropped below 25% in December.",
                 level=fl.AlertLevel.WARNING, title="Action needed"),

        fl.Select(
            fl.Group(fl.DataTable(by_region, caption="Region summary"), columns=1, label="By Region"),
            fl.Group(fl.DataTable(monthly,   caption="Monthly aggregates"), columns=1, label="Monthly"),
            fl.Group(fl.DataTable(df,        caption="All transactions"), columns=1, label="Raw Data"),
        ),

        fl.Text("## Column Profile"),
        fl.DataProfile(df),

        fl.Text("## Interactive Explorer"),
        fl.DataDive(df, x="revenue", y="margin_pct", color="region"),

        fl.Toggle(
            fl.Text("**Refresh cadence**: nightly at 02:00 UTC."),
            fl.Code("SELECT * FROM sales WHERE date >= '2023-01-01'\n", language="sql"),
            label="Methodology & sources",
        ),
    ),
    path="sales_2023.html",
    name="Sales Analysis — 2023",
    formatting=fl.Formatting(accent_color="#0f766e"),
)
```

### Multi-library charts in one report

```python
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import plotly.express as px
import folio as fl

fig_plotly = px.scatter(df, x="revenue", y="margin_pct", color="region")

fig_mpl, ax = plt.subplots()
ax.hist(df["revenue"].dropna(), bins=30)

fl.save_report(
    fl.Blocks(
        fl.Text("# Chart comparison"),
        fl.Group(
            fl.Plot(fig_plotly, caption="Interactive (Plotly)"),
            fl.Plot(fig_mpl,    caption="Static SVG (Matplotlib)"),
            columns=2,
        ),
    ),
    path="charts.html",
)
```

### Hiding methodology behind a toggle

```python
fl.Toggle(
    fl.Text("""
        **Data source**: internal data warehouse.
        **Contact**: analytics@example.com
    """),
    fl.Code("SELECT date, region, revenue FROM dw.sales\n", language="sql"),
    label="Methodology & sources",
)
```

### Tile layout (Facets Dive style)

```python
# Each (region × channel) cell is a group of packed dots coloured by product
fl.DataDive(df, x="region", y="channel", color="product", layout="tile")
```

### Jupyter inline display

```python
from IPython.display import HTML, display

display(HTML(fl.stringify_report(
    fl.Blocks(fl.Text("# Quick look"), fl.DataProfile(df)),
    name="Quick look",
)))
```

---

## Running the demo

```bash
cd /path/to/html_reporting_python
python demo/generate.py
```

This writes nine self-contained HTML files to `demo/`:

| File | Contents |
|------|----------|
| `01_blocks.html` | All text and layout blocks |
| `02_tables.html` | Static `Table` and interactive `DataTable` |
| `03_profile.html` | `DataProfile` on a mixed dataset |
| `04_datadive.html` | `DataDive` scatter explorer |
| `05_full_report.html` | Full combined KPI report |
| `06_facets_dive.html` | Tile layout comparison |
| `07_plotly.html` | Interactive Plotly charts |
| `08_matplotlib.html` | Static Matplotlib charts (inline SVG) |
| `09_theme_*.html` | CSS theme showcase (dark, corporate, minimal, ocean, warm) |
