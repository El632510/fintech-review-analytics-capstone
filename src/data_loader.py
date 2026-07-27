"""Thin CSV loading helper, kept for notebook backward-compatibility."""

from __future__ import annotations

import pandas as pd


def load_data(filepath: str) -> pd.DataFrame:
    """Load a CSV dataset into a DataFrame."""
    return pd.read_csv(filepath)
