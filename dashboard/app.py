"""
Interactive Streamlit dashboard for Customer Experience Analytics.

Run with:
    streamlit run dashboard/app.py

Data source: reads data/processed/reviews_final_for_db.csv by default
(the same file the Postgres `reviews` table is loaded from), or lets the
user upload a CSV with the same columns if that file isn't present -- so
the dashboard is demoable without a live database connection.

Explainability tab: uses SHAP's text explainer against the cached
DistilBERT sentiment pipeline to show which words pushed a specific review
toward "positive" or "negative", answering the Week 12 brief's questions
("which features matter most globally?", "why did the model make this
specific prediction?").
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.config import BANK_NAME_BY_ID, Paths  # noqa: E402

st.set_page_config(page_title="Fintech CX Analytics", layout="wide")

PATHS = Paths()


@st.cache_data
def load_reviews(uploaded_file) -> pd.DataFrame | None:
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    elif Path(PATHS.db_ready_csv).exists():
        df = pd.read_csv(PATHS.db_ready_csv)
    else:
        return None

    if "bank" not in df.columns and "bank_id" in df.columns:
        df["bank"] = df["bank_id"].map(BANK_NAME_BY_ID)

    date_col = "review_date" if "review_date" in df.columns else "date"
    if date_col in df.columns:
        df["review_date"] = pd.to_datetime(df[date_col], errors="coerce")

    return df


@st.cache_resource(show_spinner="Loading DistilBERT sentiment model...")
def get_shap_explainer():
    """Build a SHAP text Explainer wrapping the cached HF sentiment pipeline."""
    import shap

    from src.sentiment import load_sentiment_model

    model = load_sentiment_model()
    return shap.Explainer(model)


def render_overview(df: pd.DataFrame) -> None:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total reviews", len(df))
    if "sentiment_label" in df.columns:
        pos_rate = (df["sentiment_label"] == "positive").mean()
        col2.metric("Positive sentiment", f"{pos_rate:.0%}")
    if "rating" in df.columns:
        col3.metric("Avg. rating", f"{df['rating'].mean():.2f} \u2605")
    col4.metric("Banks covered", df["bank"].nunique() if "bank" in df.columns else "-")


def render_sentiment_by_bank(df: pd.DataFrame) -> None:
    if "sentiment_label" not in df.columns:
        st.info("No sentiment_label column found in this dataset.")
        return
    counts = df.groupby(["bank", "sentiment_label"]).size().reset_index(name="count")
    fig = px.bar(
        counts, x="bank", y="count", color="sentiment_label", barmode="stack",
        title="Sentiment Distribution by Bank",
        color_discrete_map={"positive": "#2E7D32", "negative": "#C62828", "neutral": "#9E9E9E"},
    )
    st.plotly_chart(fig, use_container_width=True)


def render_rating_distribution(df: pd.DataFrame) -> None:
    if "rating" not in df.columns:
        return
    fig = px.box(df, x="bank", y="rating", title="Rating Distribution by Bank", points=False)
    st.plotly_chart(fig, use_container_width=True)


def render_theme_frequency(df: pd.DataFrame) -> None:
    if "identified_theme" not in df.columns:
        st.info("No identified_theme column found in this dataset.")
        return
    theme_counts = (
        df.groupby(["bank", "identified_theme"]).size().reset_index(name="count")
    )
    fig = px.bar(
        theme_counts, x="identified_theme", y="count", color="bank", barmode="group",
        title="Theme Frequency by Bank",
    )
    fig.update_xaxes(tickangle=30)
    st.plotly_chart(fig, use_container_width=True)


def render_sentiment_trend(df: pd.DataFrame) -> None:
    if "review_date" not in df.columns or df["review_date"].isna().all():
        return
    trend = (
        df.dropna(subset=["review_date"])
        .assign(month=lambda d: d["review_date"].dt.to_period("M").dt.to_timestamp())
        .groupby(["month", "sentiment_label"])
        .size()
        .reset_index(name="count")
    )
    fig = px.line(
        trend, x="month", y="count", color="sentiment_label", markers=True,
        title="Monthly Sentiment Trend",
    )
    st.plotly_chart(fig, use_container_width=True)


def render_explainability_tab() -> None:
    st.subheader("Explain a Prediction")
    st.caption(
        "Enter any review text. SHAP highlights which words pushed the "
        "DistilBERT model's prediction toward positive (red) or negative (blue)."
    )
    example = "The app crashes every time I try to send money, very frustrating."
    text = st.text_area("Review text", value=example, height=100)

    if st.button("Explain"):
        try:
            import shap

            explainer = get_shap_explainer()
            with st.spinner("Computing SHAP values..."):
                shap_values = explainer([text])
            html = shap.plots.text(shap_values[0], display=False)
            st.components.v1.html(html, height=250, scrolling=True)
        except ImportError:
            st.warning(
                "SHAP / transformers / torch are not installed in this "
                "environment. Install the full requirements.txt to enable "
                "this tab: `pip install -r requirements.txt`."
            )
        except Exception as exc:  # noqa: BLE001
            st.error(f"Could not generate an explanation: {exc}")


def main() -> None:
    st.title("Customer Experience Analytics for Ethiopian Fintech Apps")
    st.caption("CBE · Bank of Abyssinia · Dashen Bank — Google Play review analysis")

    with st.sidebar:
        st.header("Data")
        uploaded_file = st.file_uploader("Upload reviews CSV (optional)", type="csv")

    df = load_reviews(uploaded_file)

    if df is None:
        st.warning(
            f"No dataset found at `{PATHS.db_ready_csv}`. Upload a CSV in the "
            "sidebar (columns: review_text/review, rating, bank or bank_id, "
            "sentiment_label, identified_theme, review_date) to explore the dashboard."
        )
        return

    with st.sidebar:
        st.header("Filters")
        banks = sorted(df["bank"].dropna().unique()) if "bank" in df.columns else []
        selected_banks = st.multiselect("Bank", banks, default=banks)
        if "sentiment_label" in df.columns:
            sentiments = sorted(df["sentiment_label"].dropna().unique())
            selected_sentiments = st.multiselect("Sentiment", sentiments, default=sentiments)
        else:
            selected_sentiments = None

    filtered = df.copy()
    if selected_banks:
        filtered = filtered[filtered["bank"].isin(selected_banks)]
    if selected_sentiments:
        filtered = filtered[filtered["sentiment_label"].isin(selected_sentiments)]

    render_overview(filtered)

    tab1, tab2, tab3 = st.tabs(["Sentiment & Ratings", "Themes & Trend", "Explainability"])
    with tab1:
        render_sentiment_by_bank(filtered)
        render_rating_distribution(filtered)
    with tab2:
        render_theme_frequency(filtered)
        render_sentiment_trend(filtered)
    with tab3:
        render_explainability_tab()


if __name__ == "__main__":
    main()
