"""
Transformer-based sentiment analysis using DistilBERT
(distilbert-base-uncased-finetuned-sst-2-english).

Selected over lexicon-based tools (VADER, TextBlob) for stronger contextual
understanding on ambiguous phrasing -- see docs/tool_selection_rationale.md
for the documented comparison the Week 2 brief asked for.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Protocol

from src.config import (
    HF_SENTIMENT_MODEL,
    MAX_REVIEW_CHARS_FOR_MODEL,
    NEGATIVE_LABEL,
    NEUTRAL_LABEL,
    POSITIVE_LABEL,
)


class SentimentPipeline(Protocol):
    """Structural type for a HuggingFace sentiment-analysis pipeline callable."""

    def __call__(self, text: str) -> list[dict]: ...


@dataclass(frozen=True)
class SentimentResult:
    label: str
    score: float


@lru_cache(maxsize=1)
def load_sentiment_model() -> SentimentPipeline:
    """
    Load (and cache) the DistilBERT sentiment pipeline.

    Cached with lru_cache so repeated calls -- e.g. from the Streamlit
    dashboard re-running on every widget interaction -- don't re-download
    or re-initialize the model. Import of `transformers` is deferred inside
    the function so importing this module (e.g. for unit tests) never pays
    the multi-second transformers/torch import cost unless the model is
    actually needed.
    """
    from transformers import pipeline

    return pipeline("sentiment-analysis", model=HF_SENTIMENT_MODEL)


def analyze_sentiment(review_text: str, sentiment_pipeline: SentimentPipeline) -> SentimentResult:
    """
    Classify a single review as positive/negative using the given pipeline.

    Falls back to a neutral, zero-confidence result on any pipeline error
    (e.g. malformed input) rather than raising, so a single bad review can't
    abort a batch job partway through.
    """
    try:
        truncated = str(review_text)[:MAX_REVIEW_CHARS_FOR_MODEL]
        result = sentiment_pipeline(truncated)[0]
        label = POSITIVE_LABEL if result["label"] == "POSITIVE" else NEGATIVE_LABEL
        return SentimentResult(label=label, score=float(result["score"]))
    except Exception:
        return SentimentResult(label=NEUTRAL_LABEL, score=0.0)
