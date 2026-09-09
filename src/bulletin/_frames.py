"""Dataframe intake — accept more than just pandas.

``bulletin`` renders tables and profiles against a pandas DataFrame internally,
but pandas is an optional extra (``pip install bulletin[pandas]``) and callers
should not be forced to use pandas as *their* dataframe library.

:func:`to_pandas` normalises whatever a data block is handed into a pandas
DataFrame:

* a pandas DataFrame passes straight through;
* anything implementing the dataframe interchange protocol (``__dataframe__`` —
  polars, pyarrow, modin, cuDF, vaex, …) is converted via
  ``pandas.api.interchange.from_dataframe``;
* anything else exposing ``.to_pandas()`` (pyarrow Table, polars, …) uses that;
* a plain ``dict`` / list-of-rows is passed to the ``pandas.DataFrame``
  constructor.

A native pandas-free rendering path is out of scope for now (tracked in the
development plan); this keeps the door open to other dataframe libraries without
that rewrite.
"""
from __future__ import annotations

import typing as t

from bulletin._error import BulletinError

if t.TYPE_CHECKING:
    import pandas as pd

_INSTALL_HINT = "install it with:  pip install bulletin[pandas]"


def _import_pandas() -> t.Any:
    try:
        import pandas as pd
    except ImportError as exc:  # pragma: no cover - exercised only without pandas
        raise BulletinError(f"This block needs pandas — {_INSTALL_HINT}") from exc
    return pd


def is_pandas_dataframe(obj: t.Any) -> bool:
    """True if *obj* is a pandas DataFrame, without importing pandas eagerly."""
    return any(
        f"{c.__module__}.{c.__qualname__}" == "pandas.core.frame.DataFrame"
        for c in type(obj).__mro__
    )


def looks_like_dataframe(obj: t.Any) -> bool:
    """Heuristic for auto-wrapping: does *obj* look like a tabular frame?"""
    return (
        is_pandas_dataframe(obj)
        or hasattr(obj, "__dataframe__")
        or (hasattr(obj, "to_pandas") and callable(obj.to_pandas))
    )


def to_pandas(obj: t.Any, *, block: str = "This block") -> pd.DataFrame:
    """Return *obj* as a pandas DataFrame, converting from other libraries.

    Args:
        obj: a pandas / polars / pyarrow / interchange-protocol frame, or
            something the ``pandas.DataFrame`` constructor accepts.
        block: name used in error messages (e.g. ``"DataTable"``).
    """
    pd = _import_pandas()

    if isinstance(obj, pd.DataFrame):
        return obj

    # Dataframe interchange protocol — polars, pyarrow, modin, cuDF, vaex, …
    if hasattr(obj, "__dataframe__"):
        try:
            return pd.api.interchange.from_dataframe(obj)
        except Exception:  # noqa: BLE001 - fall through to the next strategy
            pass

    # pyarrow.Table, polars.DataFrame, …
    to_pd = getattr(obj, "to_pandas", None)
    if callable(to_pd):
        return t.cast("pd.DataFrame", to_pd())

    # dict of columns / list of row dicts / numpy structured array …
    if isinstance(obj, dict | list):
        return pd.DataFrame(obj)

    raise BulletinError(
        f"{block} could not turn {type(obj).__module__}.{type(obj).__qualname__} "
        "into a table. Pass a pandas / polars / pyarrow DataFrame, an object "
        "implementing the dataframe interchange protocol, or a dict of columns."
    )
