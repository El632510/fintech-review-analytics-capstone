"""
Unit tests for src.sentiment that never load the real DistilBERT model.

Downloading a transformer model in CI is slow and flaky; instead we inject a
fake pipeline that mimics the HuggingFace `pipeline("sentiment-analysis")`
calling convention, which is exactly why analyze_sentiment() accepts the
pipeline as a parameter rather than loading it internally.
"""

from src.sentiment import analyze_sentiment


class FakePipeline:
    def __init__(self, label: str, score: float):
        self._label = label
        self._score = score

    def __call__(self, text):
        return [{"label": self._label, "score": self._score}]


class RaisingPipeline:
    def __call__(self, text):
        raise RuntimeError("model unavailable")


def test_analyze_sentiment_maps_positive_label():
    result = analyze_sentiment("Great app!", FakePipeline("POSITIVE", 0.98))
    assert result.label == "positive"
    assert result.score == 0.98


def test_analyze_sentiment_maps_negative_label():
    result = analyze_sentiment("Terrible experience", FakePipeline("NEGATIVE", 0.91))
    assert result.label == "negative"
    assert result.score == 0.91


def test_analyze_sentiment_falls_back_to_neutral_on_error():
    result = analyze_sentiment("anything", RaisingPipeline())
    assert result.label == "neutral"
    assert result.score == 0.0


def test_analyze_sentiment_truncates_long_review():
    long_review = "x" * 5000
    seen = {}

    class RecordingPipeline:
        def __call__(self, text):
            seen["length"] = len(text)
            return [{"label": "POSITIVE", "score": 0.5}]

    analyze_sentiment(long_review, RecordingPipeline())
    assert seen["length"] == 512
