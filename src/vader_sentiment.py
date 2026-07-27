"""
Lexicon-based sentiment analysis using VADER.

Kept as a lightweight, fast alternative to the transformer model (see
sentiment.py) for quick iteration, CI-friendly testing (no model download
required), and as a documented comparison point in the final report.
"""

from __future__ import annotations

from dataclasses import dataclass

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from src.config import (
    NEGATIVE_LABEL,
    NEUTRAL_LABEL,
    POSITIVE_LABEL,
    VADER_NEGATIVE_THRESHOLD,
    VADER_POSITIVE_THRESHOLD,
)

_analyzer = SentimentIntensityAnalyzer()


@dataclass(frozen=True)
class SentimentResult:
    label: str
    score: float


def classify_compound_score(compound_score: float) -> str:
    """Map a VADER compound score to a positive/negative/neutral label."""
    if compound_score >= VADER_POSITIVE_THRESHOLD:
        return POSITIVE_LABEL
    if compound_score <= VADER_NEGATIVE_THRESHOLD:
        return NEGATIVE_LABEL
    return NEUTRAL_LABEL


def analyze_vader_sentiment(review_text: str) -> SentimentResult:
    """Score a review with VADER and return a (label, compound_score) result."""
    scores = _analyzer.polarity_scores(str(review_text))
    compound_score = scores["compound"]
    return SentimentResult(label=classify_compound_score(compound_score), score=compound_score)
