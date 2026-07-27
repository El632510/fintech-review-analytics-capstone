"""
Google Play Store review scraping.

Extracted from notebooks/scraping_reviews.ipynb into a reusable, unit-
testable module. The notebook still works for exploratory runs, but
pipeline.py imports this module directly for reproducible, scriptable runs
(and for the CI-friendly test suite, which mocks scrape_bank_reviews's
dependency on the network).
"""

from __future__ import annotations

import logging

import pandas as pd
from google_play_scraper import Sort, reviews

from src.config import BankConfig, ScraperConfig

logger = logging.getLogger(__name__)


def scrape_bank_reviews(bank: BankConfig, config: ScraperConfig) -> pd.DataFrame:
    """
    Pull up to config.reviews_per_bank reviews for a single bank's app.

    Returns a DataFrame with columns: review_id, review, rating, date, bank,
    source. Logs (rather than raises) if fewer than the minimum required
    reviews come back, per the brief's "document the limitation" instruction.
    """
    result, _continuation_token = reviews(
        bank.app_id,
        lang=config.lang,
        country=config.country,
        sort=Sort.NEWEST,
        count=config.reviews_per_bank,
    )

    if len(result) < config.minimum_required_per_bank:
        logger.warning(
            "%s returned only %d reviews (minimum required: %d). "
            "Consider widening the date range or re-running later.",
            bank.display_name, len(result), config.minimum_required_per_bank,
        )

    records = [
        {
            "review_id": r["reviewId"],
            "review": r["content"],
            "rating": r["score"],
            "date": r["at"].strftime("%Y-%m-%d"),
            "bank": bank.display_name,
            "source": config.source_label,
        }
        for r in result
    ]

    return pd.DataFrame(records)


def scrape_all_banks(banks: tuple[BankConfig, ...], config: ScraperConfig) -> pd.DataFrame:
    """Scrape all configured banks and concatenate into a single DataFrame."""
    frames = [scrape_bank_reviews(bank, config) for bank in banks]
    return pd.concat(frames, ignore_index=True)
