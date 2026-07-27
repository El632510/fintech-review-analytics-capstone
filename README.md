# Customer Experience Analytics for Ethiopian Fintech Apps

![CI](https://github.com/El632510/fintech-review-analytics/actions/workflows/ci.yml/badge.svg)

A production-style analytics pipeline that turns raw Google Play Store reviews for
three Ethiopian banks into evidence-based product recommendations — plus an
interactive dashboard a bank product manager can use directly.

## Business Problem

Commercial Bank of Ethiopia (CBE), Bank of Abyssinia (BOA), and Dashen Bank
collectively receive thousands of unfiltered Google Play reviews a month. Left
unread, that feedback is noise. This project builds the pipeline to turn it into a
competitive intelligence asset: what users love, what frustrates them, and what to
build next — for each bank, backed by data.

## Solution Overview

1. **Scrape** reviews via `google-play-scraper` for all three banks (`src/scraper.py`).
2. **Clean** the raw data — dedupe, drop missing values, normalize dates — with a
   documented data-quality report (`src/preprocessing.py`).
3. **Classify sentiment** with DistilBERT (`src/sentiment.py`), compared against
   VADER (`src/vader_sentiment.py`) — see [tool selection rationale](docs/tool_selection_rationale.md).
4. **Extract themes** via keyword/TF-IDF rules mapped to 5 business categories
   (`src/themes.py`).
5. **Persist** to PostgreSQL with a two-table relational schema (`src/db.py`,
   `scripts/schema.sql`).
6. **Explore & explain** results in an interactive Streamlit dashboard with
   SHAP-based model explainability (`dashboard/app.py`).

Run any stage independently or the whole thing via `src/pipeline.py`.

## Key Results

*(from the [Week 2 final report](docs/final_report.md); re-run `src/pipeline.py` against fresh scrapes to update)*

- 1,500 reviews collected — 500 per bank — with <5% missing data
- 61.4% overall positive sentiment
- CBE leads on average rating (4.12★), then Dashen (3.92★), then BOA (3.56★)
- Login failures, OTP errors, and slow transfers are the dominant pain points across all three banks
- DistilBERT outperformed VADER on ambiguous/short reviews (see rationale doc)

## Quick Start

```bash
git clone https://github.com/El632510/fintech-review-analytics
cd fintech-review-analytics
pip install -r requirements.txt

cp .env.example .env   # fill in real DB credentials, never commit .env

python -m src.pipeline --stage all       # scrape -> sentiment -> persist
streamlit run dashboard/app.py           # explore results interactively
pytest tests/ --cov=src                  # run the test suite
```

## Project Structure

```
fintech-review-analytics/
├── .github/workflows/ci.yml     # lint + test on every push/PR
├── dashboard/app.py             # Streamlit dashboard + SHAP explainability
├── data/                        # gitignored; raw/processed CSVs land here
├── docs/
│   ├── gap_analysis.md          # Week 12 Task 1 deliverable
│   ├── tool_selection_rationale.md
│   └── final_report.md          # blog-style final report
├── notebooks/                   # exploratory analysis (scraping, sentiment, DB, insights)
├── scripts/schema.sql           # PostgreSQL DDL
├── src/
│   ├── config.py                # banks, thresholds, theme keywords, DB config (dataclasses)
│   ├── scraper.py                # Google Play scraping
│   ├── preprocessing.py          # cleaning + data-quality report
│   ├── sentiment.py               # DistilBERT (cached, lazy-loaded)
│   ├── vader_sentiment.py         # VADER comparison baseline
│   ├── nlp_pipeline.py            # tokenize/stopword/lemmatize for TF-IDF
│   ├── themes.py                  # keyword-based theme classification
│   ├── db.py                      # Postgres persistence (env-var credentials only)
│   └── pipeline.py                # end-to-end orchestrator / CLI
├── tests/                        # 24 pytest tests, CI-enforced
├── .env.example                  # copy to .env; never commit real credentials
└── requirements.txt
```

## Demo

Run `streamlit run dashboard/app.py` and open the local URL Streamlit prints. If
`data/processed/reviews_final_for_db.csv` isn't present, the sidebar lets you
upload any CSV with the same columns to explore the dashboard immediately.

## Technical Details

- **Data**: Google Play Store reviews, English-language, Feb 2025–May 2026 date range.
- **Sentiment model**: `distilbert-base-uncased-finetuned-sst-2-english` (HuggingFace),
  compared against VADER as a lexicon-based baseline.
- **Explainability**: SHAP `Explainer` wrapping the HF sentiment pipeline; shown
  per-review in the dashboard's Explainability tab.
- **Database**: PostgreSQL, two tables (`banks`, `reviews`), foreign-keyed on `bank_id`.
- **Evaluation**: sentiment aggregated by bank and by star rating; themes validated
  against manual spot-checks documented in `docs/final_report.md`.

## Future Improvements

- Swap in a multilingual model (XLM-RoBERTa / AfroXLMR) for Amharic and code-switched reviews.
- Automate weekly re-scraping via a scheduled GitHub Action feeding directly into Postgres.
- Replace rule-based theming with zero-shot classification for finer-grained issue tracking.
- Add iOS App Store reviews alongside Google Play for full user-base coverage.

## Author

Eleni Melkie · 10 Academy KAIM-9  https://www.linkedin.com/in/eleni-melkie/ · [GitHub](https://github.com/El632510)
