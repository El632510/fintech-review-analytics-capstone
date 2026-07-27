"""
End-to-end pipeline orchestrator: scrape -> preprocess -> sentiment ->
theme -> persist. Run directly (`python -m src.pipeline`) or import
individual stages.

This supersedes the notebook-driven flow (scraping_reviews.ipynb ->
sentiment_analysis.ipynb -> database_insertion.ipynb) for reproducible,
scriptable, CI-testable runs. The notebooks remain in notebooks/ for
exploratory analysis and are referenced in the final report's plots.
"""

from __future__ import annotations

import argparse
import logging

import pandas as pd

from src.config import BANK_ID_BY_NAME, BANKS, DBConfig, Paths, ScraperConfig
from src.db import get_connection, insert_banks, insert_reviews
from src.nlp_pipeline import preprocess_text
from src.preprocessing import preprocess_reviews
from src.scraper import scrape_all_banks
from src.sentiment import analyze_sentiment, load_sentiment_model
from src.themes import identify_theme

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def run_scrape_and_clean(
    paths: Paths = Paths(),
    scraper_config: ScraperConfig = ScraperConfig(),
) -> pd.DataFrame:
    raw_df = scrape_all_banks(BANKS, scraper_config)
    cleaned_df, report = preprocess_reviews(raw_df)
    logger.info(
        "Scraped %d rows -> cleaned %d rows (missing_dropped=%d, duplicates_dropped=%d, missing_rate=%.2f%%)",
        report.initial_rows, report.final_rows, report.missing_dropped,
        report.duplicates_dropped, report.missing_rate * 100,
    )
    cleaned_df.to_csv(paths.scraped_csv, index=False)
    return cleaned_df


def run_sentiment_and_themes(cleaned_df: pd.DataFrame, paths: Paths = Paths()) -> pd.DataFrame:
    model = load_sentiment_model()

    results = cleaned_df["review"].apply(lambda text: analyze_sentiment(text, model))
    cleaned_df = cleaned_df.copy()
    cleaned_df["sentiment_label"] = [r.label for r in results]
    cleaned_df["sentiment_score"] = [r.score for r in results]
    cleaned_df["identified_theme"] = cleaned_df["review"].apply(identify_theme)
    cleaned_df["processed_review"] = cleaned_df["review"].apply(preprocess_text)

    cleaned_df.to_csv(paths.sentiment_theme_csv, index=False)
    return cleaned_df


def run_persist(processed_df: pd.DataFrame) -> None:
    db_ready = processed_df.rename(columns={"review": "review_text", "date": "review_date"}).copy()
    db_ready["bank_id"] = db_ready["bank"].map(BANK_ID_BY_NAME)

    with get_connection(DBConfig()) as conn:
        insert_banks(conn)
        insert_reviews(conn, db_ready)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the fintech review analytics pipeline.")
    parser.add_argument(
        "--stage",
        choices=["scrape", "sentiment", "persist", "all"],
        default="all",
        help="Which stage to run (default: all).",
    )
    args = parser.parse_args()

    paths = Paths()

    if args.stage in ("scrape", "all"):
        cleaned_df = run_scrape_and_clean(paths)
    else:
        cleaned_df = pd.read_csv(paths.scraped_csv)

    if args.stage in ("sentiment", "all"):
        processed_df = run_sentiment_and_themes(cleaned_df, paths)
    else:
        processed_df = pd.read_csv(paths.sentiment_theme_csv)

    if args.stage in ("persist", "all"):
        run_persist(processed_df)


if __name__ == "__main__":
    main()
