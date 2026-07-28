# Week 12 Gap Analysis & Improvement Plan

**Project selected:** *Customer Experience Analytics for Ethiopian Fintech Apps* (Week 2)

**Why this project:** It's the most complete end-to-end pipeline in my portfolio —
scraping, NLP, a relational database, and business-facing recommendations — and it
targets a finance-sector audience directly (three Ethiopian banks), which matches
this week's brief. It also had the clearest, highest-leverage gaps to close.

## Gap Analysis Checklist

| Category | Question | Status (before) | Status (after) |
|---|---|---|---|
| **Code Quality** | Is the code modular and well-organized? | Partial — logic lived mostly inline in notebooks | Yes — `src/` package with one responsibility per module (`scraper`, `preprocessing`, `sentiment`, `vader_sentiment`, `themes`, `nlp_pipeline`, `db`, `pipeline`, `config`) |
| | Are there type hints on functions? | No | Yes — all `src/` functions and dataclasses are typed |
| | Is there a clear project structure? | Yes (already good) | Kept, added `dashboard/` and `docs/` |
| **Testing** | Are there unit tests for core functions? | No — one placeholder test (`assertEqual(1+1, 2)`) | Yes — 24 tests across 5 files covering preprocessing, theming, VADER, config, and sentiment (mocked model boundary, no network/model download required) |
| | Do tests run automatically on push? | Partial — a CI workflow existed but installed a broken `requirements.txt` | Yes — `ci.yml` lints with ruff and runs pytest with coverage on every push/PR |
| **Documentation** | Is the README comprehensive? | Partial — covered scraping and DB schema, missing business framing, quick start, and results | Yes — rewritten to the Week 12 template (business problem, solution, results, quick start, structure, technical details, future work) |
| | Are there docstrings on functions? | No | Yes — every public function/class has a docstring |
| **Reproducibility** | Can someone else run this project? | No — `requirements.txt` was UTF-16 encoded and missing nearly every real dependency (no transformers, torch, nltk, psycopg2, or pytest); DB credentials were hardcoded to one machine | Yes — fixed `requirements.txt`, `.env.example` for config, `pipeline.py` as a single runnable entry point |
| | Are dependencies in requirements.txt? | No (file was corrupted/incomplete) | Yes |
| **Reproducibility / Security** | Are credentials kept out of source control? | **No — a plaintext Postgres password was committed inside `database_insertion.ipynb`** | Yes — `DBConfig` reads from environment variables only; a regression test (`test_db_config_never_hardcodes_a_password`) guards against recurrence |
| **Visualization** | Is there an interactive way to explore results? | No — static matplotlib plots in a notebook | Yes — Streamlit dashboard with filters, 4 chart types, and a model-explainability tab |
| **Business Impact** | Is the problem clearly articulated? | Yes (final report was strong here) | Kept, tightened for the blog-style report |
| | Are success metrics defined? | Partial | Yes — reproduced in the updated final report's Key Results section |

## Prioritized Improvement Plan

Selected 5 high-impact improvements, ranked by (a) risk closed, (b) portfolio impact for a finance audience, (c) feasibility within the week:

| # | Improvement | Time estimate | Why it matters to a finance reviewer |
|---|---|---|---|
| 1 | Remove hardcoded DB credentials; move to env-var config | 1–2 hrs | Security/reliability is the #1 thing finance recruiters flag — a leaked credential in a public repo is disqualifying |
| 2 | Fix `requirements.txt` and add a proper CI pipeline (lint + test) | 1–2 hrs | "Can someone else run this" is the first thing a hiring manager checks; a broken CI badge signals unreliable engineering |
| 3 | Refactor `src/` with type hints, dataclasses, and named constants; write 20+ unit tests | 4–5 hrs | Demonstrates engineering rigor, not just data science — directly addresses "reliability and reducing risk" |
| 4 | Build an interactive Streamlit dashboard | 3–4 hrs | Turns a static report into a tool a non-technical product manager can actually use — "immediately understandable to non-technical stakeholders" |
| 5 | Add SHAP-based explainability to the sentiment model | 2–3 hrs | Finance is a regulated, trust-sensitive domain; being able to show *why* the model called a review negative is a differentiator most portfolio projects skip |

Total estimated effort: ~12–16 hours, matching the one-week window.
