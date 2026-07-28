from src.vader_sentiment import analyze_vader_sentiment, classify_compound_score


def test_classify_compound_score_boundaries():
    assert classify_compound_score(0.06) == "positive"
    assert classify_compound_score(-0.06) == "negative"
    assert classify_compound_score(0.0) == "neutral"


def test_analyze_vader_sentiment_positive_review():
    result = analyze_vader_sentiment("I absolutely love this app, it's fantastic!")
    assert result.label == "positive"
    assert result.score > 0


def test_analyze_vader_sentiment_negative_review():
    result = analyze_vader_sentiment("Terrible app, it crashes constantly and I hate it.")
    assert result.label == "negative"
    assert result.score < 0
