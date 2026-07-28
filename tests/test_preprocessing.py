import pandas as pd
import pytest

from src.preprocessing import preprocess_reviews


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "review_id": ["r1", "r2", "r2", "r3"],
            "review": ["Great app", "Crashes often", "Crashes often", None],
            "rating": [5, 2, 2, 3],
            "date": ["2026-01-05", "2026-02-10", "2026-02-10", "2026-03-01"],
            "bank": ["CBE", "BOA", "BOA", "Dashen"],
            "source": ["Google Play"] * 4,
        }
    )


def test_drops_rows_missing_review_or_rating():
    cleaned, report = preprocess_reviews(_sample_df())
    assert cleaned["review"].isnull().sum() == 0
    assert report.missing_dropped == 1


def test_drops_duplicate_review_ids():
    cleaned, report = preprocess_reviews(_sample_df())
    assert cleaned["review_id"].duplicated().sum() == 0
    assert report.duplicates_dropped == 1


def test_normalizes_date_format():
    cleaned, _ = preprocess_reviews(_sample_df())
    assert all(cleaned["date"].str.match(r"^\d{4}-\d{2}-\d{2}$"))


def test_missing_required_column_raises():
    df = pd.DataFrame({"rating": [5, 4]})
    with pytest.raises(ValueError):
        preprocess_reviews(df)


def test_cleaning_report_missing_rate():
    cleaned, report = preprocess_reviews(_sample_df())
    assert report.initial_rows == 4
    assert report.final_rows == len(cleaned)
    assert 0 <= report.missing_rate <= 1
