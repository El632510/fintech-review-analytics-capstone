# Customer Experience Analytics for Ethiopian Fintech Apps
**Eleni Melkie · 10 Academy KAIM-9 · Week 2 findings, Week 12 capstone hardening**

## Executive Summary

Ethiopia's mobile banking sector is expanding rapidly, with millions of users
turning to apps from the Commercial Bank of Ethiopia (CBE), Bank of Abyssinia
(BOA), and Dashen Bank for everyday financial services. Yet beneath the surface
of growth lies a wealth of unfiltered customer feedback — and most of it goes
unread.

This project builds a full-stack customer experience analytics pipeline that
transforms raw Google Play Store reviews into evidence-based product insights
bank teams can act on: scraping and cleaning review data, classifying sentiment
and themes with NLP, persisting results in a relational database, and
surfacing insights through an interactive dashboard.

**Key headline findings** (from the original Week 2 data collection):

- 1,500 reviews collected — 500 per bank — with a 61.4% positive sentiment rate overall
- CBE leads in average rating (4.12★), followed by Dashen Bank (3.92★) and BOA (3.56★)
- Login failures, OTP errors, and slow performance are the dominant pain points across all three banks
- DistilBERT delivered more reliable sentiment classification than lexicon-based alternatives on ambiguous reviews
- Five business themes identified: Account Access Issues, Transaction Performance, UI & Design, Customer Support, Feature Requests

**What changed in the Week 12 capstone pass:** the analysis itself is unchanged,
but the *engineering* behind it was hardened for production use — see
"Capstone Engineering Improvements" below.

## Data Collection Methodology & Quality Assessment

Reviews were collected using the `google-play-scraper` Python library against
each bank's real Play Store app ID, over the date range February 2025–May
2026. For each review: text, star rating (1–5), date, bank/app name, and
source platform.

**Preprocessing:** duplicate removal (by `review_id`), missing-value handling
(rows with null review text or rating dropped, counts documented), and date
normalization to `YYYY-MM-DD`.

| Metric | Value |
|---|---|
| Total reviews | 1,500 |
| Per bank | 500 each |
| Missing data rate | <3% |
| Date range | Feb 2025 – May 2026 |
| Source | Google Play Store |

**Limitations:** Google Play pagination constraints, review-availability
variation across scraping sessions, and non-English (primarily Amharic)
reviews that required careful handling during NLP processing.

## Sentiment Analysis: Methodology, Tools & Results

Two approaches were evaluated: **VADER** (rule-based lexicon) and
**DistilBERT** (`distilbert-base-uncased-finetuned-sst-2-english`,
transformer-based). VADER is fast and interpretable but struggles with
contextually nuanced language — a review like *"Works, but barely"* scores
ambiguously with VADER but gets a confident negative label from DistilBERT.
Full rationale: [`docs/tool_selection_rationale.md`](tool_selection_rationale.md).

| Bank | Avg Rating | Sentiment |
|---|---|---|
| Commercial Bank of Ethiopia | 4.12★ | 67% Positive |
| Bank of Abyssinia | 3.56★ | 53% Positive |
| Dashen Bank | 3.92★ | 64% Positive |

Overall, 921 of 1,500 reviews (61.4%) were classified positive. CBE showed the
strongest sentiment profile; BOA the most negative, with recurring complaints
about transaction reliability and customer support.

## Thematic Analysis: Findings & Theme Summaries

TF-IDF was applied after tokenization, stop-word removal, and lemmatization
(spaCy/NLTK), extracting unigrams and bigrams ("login error", "slow transfer",
"good interface"), then grouped into five business themes.

| Theme | Count | Sample Keywords |
|---|---|---|
| Account Access Issues | 27 | login error, OTP failed, cannot login, verification issue |
| Transaction Performance | 105 | slow transfer, payment delay, transaction failed, timeout |
| UI & Design | 51 | easy to use, good interface, clean design, user friendly |
| Customer Support | 50 | no response, support problem, unhelpful, slow service |
| Feature Requests | 47 | fingerprint login, budgeting tools, dark mode, notifications |

**Bank-specific highlights:**

- **CBE** — dominant theme: Transaction Performance (slow transfers); strong positive signal on convenience and accessibility.
- **BOA** — dominant theme: Customer Support (hard to reach, slow resolution); secondary: Transaction Performance.
- **Dashen** — dominant theme: Transaction Performance, with significant Account Access Issues; strong UI & Design scores when the app functions.

## Database Design Overview

Processed data is persisted in PostgreSQL (`bank_reviews` database), with
`banks` (metadata) and `reviews` (processed data, foreign-keyed on `bank_id`)
tables — see `scripts/schema.sql`. All 1,500 reviews were inserted via the
now-refactored `src/db.py`, using idempotent `ON CONFLICT DO NOTHING` inserts
so pipeline re-runs are safe.

## Insights, Visualizations & Bank-Specific Recommendations

Across all three banks, the pattern is consistent: when the app works,
users are highly satisfied; when it fails — even briefly — the resulting
frustration generates disproportionate negative reviews.

**Commercial Bank of Ethiopia — Maintain the Lead**
Drivers: fast transactions, widespread adoption (4.12★). Pain points: OTP
verification failures, slow loading during peak transfers.
1. Deploy redundant OTP delivery infrastructure (SMS + in-app TOTP fallback).
2. Introduce proactive performance monitoring to catch transfer slowdowns before they hit users.

**Bank of Abyssinia — Close the Gap**
Drivers: clean, simple interface; mobile-first convenience. Pain points:
highest transaction failure rate, widely criticized customer support (3.56★).
1. Invest in backend transaction reliability — end-to-end retry logic and user-facing failure notifications.
2. Integrate an in-app AI chatbot for first-line support to reduce wait times.

**Dashen Bank — Fix and Fortify**
Drivers: good UI & design, positive overall experience. Pain points:
recurring bugs, app freezing, slow response times (3.92★).
1. Establish a bug-triage process using review theme data, prioritizing Account Access Issues.
2. Introduce app performance benchmarks (load-time SLAs) and a public improvement roadmap.

## Capstone Engineering Improvements (Week 12)

The Week 2 analysis was sound; the codebase behind it was notebook-first and
had real production risk. This pass focused on closing that gap:

- **Removed a hardcoded, plaintext Postgres password** that had been committed
  inside `database_insertion.ipynb`. Credentials now load exclusively from
  environment variables via `src/config.py`'s `DBConfig`, with a regression
  test guarding against recurrence.
- **Fixed `requirements.txt`**, which was UTF-16 encoded and missing nearly
  every real dependency (transformers, torch, nltk, psycopg2, pytest). A
  fresh clone can now actually be installed and run.
- **Refactored `src/`** into typed, documented, single-responsibility modules
  with named constants replacing magic strings, and a runnable
  `src/pipeline.py` CLI tying every stage together.
- **Added a real test suite** — 24 pytest tests covering preprocessing,
  theming, VADER, config, and sentiment-label mapping (with the DistilBERT
  model boundary mocked, so CI never needs to download a transformer model).
- **Wired up CI** (`ci.yml`) to lint (ruff) and test on every push/PR.
- **Built an interactive Streamlit dashboard** (`dashboard/app.py`) so a
  non-technical product manager can filter by bank/sentiment and explore
  sentiment distribution, rating spread, theme frequency, and monthly trend
  without opening a notebook.
- **Added SHAP-based explainability**, so any single review's sentiment
  prediction can be inspected word-by-word — important in a regulated,
  trust-sensitive domain like finance.

## Ethical Considerations & Limitations

**Ethical considerations:** only fields necessary for analysis were retained
(no reviewer usernames used); DistilBERT was pre-trained on English data, so
Amharic or code-switched reviews may be misclassified; Google Play's terms of
service permit scraping publicly visible review data for analytical purposes;
all insights are aggregate, with no individual-reviewer-level analysis.

**Limitations:** an English-only model under-serves Amharic reviewers (a
multilingual model like XLM-RoBERTa would help); Play Store reviews skew
bimodal (very happy or very unhappy users post more); the Feb 2025–May 2026
snapshot may not reflect recent product changes; 81.3% of reviews still fell
into "Other" under the current rule-based theme taxonomy, leaving room for a
zero-shot classifier to improve coverage; scraping rate limits constrained
retrieval of older historical reviews.

## Suggested Next Steps

**Immediate:** deploy a multilingual sentiment model (XLM-RoBERTa/AfroXLMR)
for Amharic coverage; expand the theme taxonomy via zero-shot classification;
automate weekly scraping directly into Postgres.

**Medium-term:** integrate iOS App Store reviews for full user-base coverage;
add Named Entity Recognition to identify specific product features mentioned
in reviews; deploy the dashboard for bank product managers to use directly.

**Strategic:** extend to all major Ethiopian fintech apps for cross-sector
competitive benchmarking; connect the pipeline to bank support systems to flag
high-confidence negative reviews in real time; correlate sentiment patterns
with retention data to build predictive churn indicators.

---
*Eleni Melkie · 10 Academy KAIM-9 · Week 2 analysis, Week 12 capstone*
