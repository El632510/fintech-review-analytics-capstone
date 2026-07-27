"""
Centralized configuration for the fintech-review-analytics pipeline.

Replaces the magic strings and hardcoded credentials that were previously
scattered across notebooks (e.g. a plaintext Postgres password inside
database_insertion.ipynb) with typed, environment-driven configuration
objects. This is the single source of truth for bank metadata, sentiment
thresholds, theme keywords, and database connection settings.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

# --------------------------------------------------------------------------- #
# Bank / scraping configuration
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class BankConfig:
    """Metadata for a single bank's mobile app on the Google Play Store."""

    key: str
    display_name: str
    app_id: str


# The three banks in scope for this analysis. Adding a fourth bank (e.g. for
# competitive benchmarking, per the Week 2 report's "Strategic Opportunities")
# is a one-line change here instead of a hunt through notebooks.
BANKS: tuple[BankConfig, ...] = (
    BankConfig("cbe", "Commercial Bank of Ethiopia", "com.combanketh.mobilebanking"),
    BankConfig("boa", "Bank of Abyssinia", "com.boa.boaMobileBanking"),
    BankConfig("dashen", "Dashen Bank", "com.dashen.dashensuperapp"),
)

BANK_ID_BY_NAME: dict[str, int] = {
    bank.display_name: idx + 1 for idx, bank in enumerate(BANKS)
}
BANK_NAME_BY_ID: dict[int, str] = {v: k for k, v in BANK_ID_BY_NAME.items()}


@dataclass(frozen=True)
class ScraperConfig:
    """Parameters controlling how many reviews to pull and from where."""

    reviews_per_bank: int = 500
    minimum_required_per_bank: int = 400
    lang: str = "en"
    country: str = "et"
    source_label: str = "Google Play"


# --------------------------------------------------------------------------- #
# Sentiment analysis configuration
# --------------------------------------------------------------------------- #

POSITIVE_LABEL = "positive"
NEGATIVE_LABEL = "negative"
NEUTRAL_LABEL = "neutral"

HF_SENTIMENT_MODEL = "distilbert-base-uncased-finetuned-sst-2-english"
MAX_REVIEW_CHARS_FOR_MODEL = 512  # DistilBERT's max token window is limited; truncate long reviews.

VADER_POSITIVE_THRESHOLD = 0.05
VADER_NEGATIVE_THRESHOLD = -0.05


# --------------------------------------------------------------------------- #
# Thematic analysis configuration
# --------------------------------------------------------------------------- #

# Centralizing the keyword lists (previously inline if/elif branches in
# themes.py) makes it possible to unit test theme coverage and to extend the
# taxonomy without touching function logic.
THEME_KEYWORDS: dict[str, tuple[str, ...]] = {
    "Account Access Issues": (
        "login", "log in", "password", "otp", "account locked", "verification",
    ),
    "Transaction Performance": (
        "transfer", "transaction", "payment", "slow", "delay", "failed",
    ),
    "UI & Design": (
        "interface", "design", "ui", "easy to use", "layout",
    ),
    "Customer Support": (
        "support", "service", "help", "response", "customer care",
    ),
    "Feature Requests": (
        "feature", "update", "fingerprint", "dark mode", "add",
    ),
}
OTHER_THEME = "Other"

TFIDF_MAX_FEATURES = 50
TFIDF_NGRAM_RANGE = (1, 2)


# --------------------------------------------------------------------------- #
# Database configuration
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class DBConfig:
    """
    Postgres connection settings, read from environment variables.

    No credentials are hardcoded anywhere in this project. Copy .env.example
    to .env (which is gitignored) and fill in real values, or export the
    variables in your shell / CI secrets.
    """

    host: str = field(default_factory=lambda: os.getenv("DB_HOST", "localhost"))
    port: int = field(default_factory=lambda: int(os.getenv("DB_PORT", "5432")))
    database: str = field(default_factory=lambda: os.getenv("DB_NAME", "bank_reviews"))
    user: str = field(default_factory=lambda: os.getenv("DB_USER", "postgres"))
    password: str = field(default_factory=lambda: os.getenv("DB_PASSWORD", ""))

    def as_dsn_kwargs(self) -> dict:
        """Return kwargs suitable for psycopg2.connect(**kwargs)."""
        return {
            "host": self.host,
            "port": self.port,
            "database": self.database,
            "user": self.user,
            "password": self.password,
        }


# --------------------------------------------------------------------------- #
# File paths
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class Paths:
    raw_dir: str = "data/raw"
    processed_dir: str = "data/processed"
    scraped_csv: str = "data/raw/bank_reviews_cleaned.csv"
    sentiment_theme_csv: str = "data/processed/task2_final_results.csv"
    db_ready_csv: str = "data/processed/reviews_final_for_db.csv"
