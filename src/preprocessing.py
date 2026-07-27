"""
Cleaning and preprocessing for scraped Google Play review data.

Refactored from the original script to (a) add type hints and docstrings,
(b) return a small, testable data-quality report alongside the cleaned
DataFrame instead of only printing to stdout, and (c) raise a clear error
if required columns are missing rather than failing deep inside pandas.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

REQUIRED_COLUMNS: tuple[str, ...] = ("review", "rating", "date", "bank", "source")


@dataclass(frozen=True)
class CleaningReport:
    """Summary of what preprocessing removed, for README / report documentation."""

    initial_rows: int
    missing_dropped: int
    duplicates_dropped: int
    final_rows: int

    @property
    def missing_rate(self) -> float:
        if self.initial_rows == 0:
            return 0.0
        return self.missing_dropped / self.initial_rows


def preprocess_reviews(df: pd.DataFrame) -> tuple[pd.DataFrame, CleaningReport]:
    """
    Clean a raw scraped-reviews DataFrame.

    Steps:
        1. Drop rows missing review text or rating.
        2. Drop duplicate reviews (by review_id, if present).
        3. Normalize the `date` column to YYYY-MM-DD.

    Returns:
        (cleaned_df, CleaningReport) - the report gives the counts needed
        for the "document counts" KPI in the Task 1 brief instead of relying
        on scattered print statements.
    """
    missing_required = [c for c in ("review", "rating") if c not in df.columns]
    if missing_required:
        raise ValueError(f"Missing required column(s): {missing_required}")

    initial_rows = len(df)

    cleaned = df.dropna(subset=["review", "rating"])
    missing_dropped = initial_rows - len(cleaned)

    before_dedup = len(cleaned)
    if "review_id" in cleaned.columns:
        cleaned = cleaned.drop_duplicates(subset=["review_id"])
    else:
        dedup_cols = ["review", "bank"] if "bank" in cleaned.columns else ["review"]
        cleaned = cleaned.drop_duplicates(subset=dedup_cols)
    duplicates_dropped = before_dedup - len(cleaned)

    if "date" in cleaned.columns:
        cleaned = cleaned.copy()
        cleaned["date"] = pd.to_datetime(cleaned["date"]).dt.strftime("%Y-%m-%d")

    report = CleaningReport(
        initial_rows=initial_rows,
        missing_dropped=missing_dropped,
        duplicates_dropped=duplicates_dropped,
        final_rows=len(cleaned),
    )

    return cleaned, report
