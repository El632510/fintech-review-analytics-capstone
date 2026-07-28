# Sentiment Tool Selection: DistilBERT vs. VADER

Two approaches were evaluated for classifying review sentiment:

**VADER** (`vaderSentiment`) — a lexicon-based, rule-driven scorer. Fast (no model
load), fully interpretable (every word's contribution is inspectable), and
requires no GPU or model download. It struggles with context: negation, sarcasm,
and short/ambiguous phrasing (e.g. "Works, but barely") often score close to
neutral even when a human reader would call them negative.

**DistilBERT** (`distilbert-base-uncased-finetuned-sst-2-english`) — a
transformer model fine-tuned on the Stanford Sentiment Treebank. It captures
context (word order, negation, mixed sentiment within one sentence) far better
than a lexicon, at the cost of needing `transformers`/`torch` and a one-time
model download (~260MB), and being effectively a black box without extra
tooling — which is why this project pairs it with SHAP for explainability.

## Decision

DistilBERT is the primary model used in `src/pipeline.py` and the dashboard.
VADER is kept in `src/vader_sentiment.py` as a fast, dependency-light
comparison baseline and as a sanity check — if the two models disagree
sharply on a large batch of reviews, that's a signal worth investigating
before trusting the aggregate numbers.

## Engineering implication

Because DistilBERT is comparatively slow and requires a model download,
`src/sentiment.py` lazy-imports `transformers` inside `load_sentiment_model()`
and caches the loaded pipeline (`functools.lru_cache`, and `st.cache_resource`
in the dashboard). This means:

- Importing `src.sentiment` for unit tests never pays the `transformers`/`torch`
  import cost, since `analyze_sentiment()` takes the pipeline as a parameter
  and tests inject a lightweight fake (see `tests/test_sentiment.py`).
- The dashboard only downloads/loads the real model once per session, not on
  every widget interaction.
- CI does not need to install `torch`/`transformers` at all to validate the
  sentiment-mapping logic, keeping the pipeline fast and reliable.
