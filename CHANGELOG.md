# Changelog

All notable changes to `briefing` are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!-- At release time: rename [Unreleased] to the version, add the date, and
     open a fresh [Unreleased] section above it. -->

## [Unreleased]

### Added

- `briefing.lab` subpackage for custom-visualisation blocks (`DataProfile`,
  `DataDive`), installed via `pip install briefing[lab]`.
- Opt-in extras for every `Plot` backend: `briefing[plotly]`, `[altair]`,
  `[bokeh]`, `[matplotlib]`, and `[charts]` for all four.
- Renderer registry (`@renderer_for` + MRO lookup) so block subclasses inherit
  a renderer.
- Byte-reproducible output via `render_report(now=...)` / `SOURCE_DATE_EPOCH`.
- `to_pandas()` dataframe intake: accepts polars, pyarrow, `__dataframe__`
  objects and dicts in addition to pandas.
- `py.typed` marker; the package ships inline type hints.
- Apache-2.0 `LICENSE` file; packaging metadata for PyPI (authors, project
  URLs, Trusted Publishing release workflow).

### Changed

- **pandas is now optional** — `pip install briefing[pandas]`; `import briefing`
  no longer imports pandas.
- The core install has zero visualisation-library dependencies. `Plot` imports a
  plotting library only when handed a figure from it.
- `DataDive`'s JavaScript is inlined only when a `DataDive` block is present
  (core `report.js` shrank from ~530 to ~160 lines).

### Deprecated

- `briefing.DataProfile` / `briefing.DataDive` — use `briefing.lab.DataProfile` /
  `briefing.lab.DataDive`. The top-level aliases warn and will be removed after
  0.2.
- `briefing.Blocks` / `BaseBlock` / `save_report` / `stringify_report` — use
  `Briefing` / `Block` / `save` / `stringify`. Removed after 0.2.

### Fixed

- Package now imports and runs on Python 3.11 (a PEP 701 f-string had made
  `datadive.py` 3.12-only).

## [0.1.0]

- Initial internal baseline: block grammar, self-contained HTML renderer,
  `Plot` / `Table` / `DataTable` / `DataProfile` / `DataDive`, theming.

[Unreleased]: https://github.com/jeanmidevacc/folio/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/jeanmidevacc/folio/releases/tag/v0.1.0
