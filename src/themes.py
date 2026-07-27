"""
Rule-based thematic classification of review text.

Keyword lists live in src.config.THEME_KEYWORDS so the taxonomy can be
extended (e.g. via zero-shot classification results) without touching this
function's control flow. Theme precedence matches the original design:
first matching theme (in dict insertion order) wins.
"""

from __future__ import annotations

from src.config import OTHER_THEME, THEME_KEYWORDS


def identify_theme(review: str) -> str:
    """
    Classify a single review into one of the business themes defined in
    THEME_KEYWORDS, or OTHER_THEME if no keyword matches.
    """
    text = str(review).lower()

    for theme, keywords in THEME_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return theme

    return OTHER_THEME
