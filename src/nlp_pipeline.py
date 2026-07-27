"""
Text-normalization pipeline used ahead of TF-IDF keyword extraction:
lowercase -> tokenize -> drop stopwords/non-alphabetic tokens -> lemmatize.
"""

from __future__ import annotations

from functools import lru_cache

import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

_REQUIRED_NLTK_RESOURCES = (
    ("tokenizers/punkt_tab", "punkt_tab"),
    ("corpora/stopwords", "stopwords"),
    ("corpora/wordnet", "wordnet"),
)


def ensure_nltk_resources() -> None:
    """Download required NLTK corpora if not already present (idempotent)."""
    for path, package in _REQUIRED_NLTK_RESOURCES:
        try:
            nltk.data.find(path)
        except LookupError:
            nltk.download(package, quiet=True)


@lru_cache(maxsize=1)
def _stop_words() -> set[str]:
    ensure_nltk_resources()
    from nltk.corpus import stopwords

    return set(stopwords.words("english"))


@lru_cache(maxsize=1)
def _lemmatizer() -> WordNetLemmatizer:
    ensure_nltk_resources()
    return WordNetLemmatizer()


def preprocess_text(text: str) -> str:
    """
    Normalize free text for TF-IDF: lowercase, tokenize, strip stopwords
    and non-alphabetic tokens, lemmatize, and rejoin into a string.
    """
    ensure_nltk_resources()

    lowered = str(text).lower()
    tokens = word_tokenize(lowered)

    stop_words = _stop_words()
    lemmatizer = _lemmatizer()

    filtered_tokens = [w for w in tokens if w.isalpha() and w not in stop_words]
    lemmatized_tokens = [lemmatizer.lemmatize(w) for w in filtered_tokens]

    return " ".join(lemmatized_tokens)
