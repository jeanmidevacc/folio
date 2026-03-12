"""Shared pytest fixtures for the folio test suite."""
from __future__ import annotations

import pytest
import pandas as pd


# ── DataFrame fixtures ────────────────────────────────────────────────────────


@pytest.fixture
def df_mixed() -> pd.DataFrame:
    """DataFrame covering all common dtype categories, with some nulls."""
    import numpy as np

    rng = np.random.default_rng(42)
    n = 200
    categories = ["alpha", "beta", "gamma", "delta"]

    df = pd.DataFrame(
        {
            "id": range(n),
            "numeric_int": rng.integers(0, 1000, n),
            "numeric_float": rng.uniform(0.0, 100.0, n),
            "category": pd.Categorical([categories[i % 4] for i in range(n)]),
            "text": [f"item_{i}" for i in range(n)],
            "flag": [bool(i % 2) for i in range(n)],
            "nullable_int": [None if i % 10 == 0 else int(i) for i in range(n)],
            "nullable_float": [None if i % 7 == 0 else float(i) * 1.5 for i in range(n)],
            "timestamp": pd.date_range("2024-01-01", periods=n, freq="D"),
        }
    )
    return df


@pytest.fixture
def df_empty() -> pd.DataFrame:
    """Empty DataFrame — zero rows, zero columns."""
    return pd.DataFrame()


@pytest.fixture
def df_single_row() -> pd.DataFrame:
    """DataFrame with exactly one row."""
    return pd.DataFrame({"a": [1], "b": ["hello"], "c": [3.14]})


@pytest.fixture
def df_all_null() -> pd.DataFrame:
    """DataFrame where every value is null."""
    import numpy as np

    return pd.DataFrame(
        {
            "x": [np.nan, np.nan, np.nan],
            "y": [None, None, None],
        }
    )


@pytest.fixture
def df_large() -> pd.DataFrame:
    """DataFrame with 15 000 rows — triggers sampling / truncation warnings."""
    import numpy as np

    rng = np.random.default_rng(0)
    return pd.DataFrame(
        {
            "a": rng.integers(0, 100, 15_000),
            "b": rng.uniform(0, 1, 15_000),
            "c": [f"cat_{i % 5}" for i in range(15_000)],
        }
    )


@pytest.fixture
def df_constant() -> pd.DataFrame:
    """DataFrame where every column has only one unique value (zero-variance)."""
    return pd.DataFrame({"x": [42] * 50, "y": ["same"] * 50})
