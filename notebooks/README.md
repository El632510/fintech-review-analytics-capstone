# Fintech Review Analytics

## Project Overview

This project analyzes customer reviews from Ethiopian mobile banking applications on the Google Play Store. The goal is to collect, clean, analyze, and visualize customer feedback to generate actionable business insights for fintech product teams.

The analysis focuses on:

- Commercial Bank of Ethiopia (CBE)
- Bank of Abyssinia (BOA)
- Dashen Bank

---

# Task 1: Data Collection and Preprocessing

## Objective

To scrape user reviews from Google Play Store applications, preprocess the data, and prepare a clean dataset for sentiment and thematic analysis.

---

# Scraping Methodology

The reviews were collected using the Python library:

- `google-play-scraper`

The scraper extracted the following fields:

- Review text
- Rating (1–5)
- Review date
- Bank/app name
- Source platform

The data was collected from the Google Play Store for each banking application.

---

# Tools and Libraries Used

- Python 3.10
- pandas
- google-play-scraper
- Jupyter Notebook

---

# Data Preprocessing Steps

The following preprocessing steps were applied:

1. Removed duplicate reviews using review IDs.
2. Removed rows with missing review text or ratings.
3. Normalized review dates to `YYYY-MM-DD` format.
4. Saved cleaned datasets as CSV files.

---

# Date Range

Reviews were scraped using the latest available reviews returned by the Google Play Store API at the time of collection.

Collection period:
- May 2026

---

# Limitations Encountered

Some limitations were encountered during scraping:

- Google Play Store may limit the number of accessible reviews.
- Some reviews contained very short or unclear text.
- Certain reviews were written in mixed languages.
- Review availability may change over time as new reviews are posted or removed.

If fewer than the target number of reviews are available, the date range may be expanded to retrieve additional reviews.

---

# Project Structure

```text
fintech-review-analytics/
├── data/
├── notebooks/
├── scripts/
├── src/
├── tests/
└── .github/workflows/