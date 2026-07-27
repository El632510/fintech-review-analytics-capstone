"""
PostgreSQL persistence layer.

Replaces the original database_insertion.ipynb approach -- which connected
with a hardcoded plaintext password (psycopg2.connect(..., password="E@1992"))
committed to a notebook -- with a parameterized connection built from
src.config.DBConfig (environment-variable driven, see .env.example).
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from contextlib import contextmanager

import pandas as pd
import psycopg2
from psycopg2.extensions import connection as PGConnection

from src.config import BANK_ID_BY_NAME, BANKS, DBConfig

logger = logging.getLogger(__name__)

INSERT_BANK_SQL = """
    INSERT INTO banks (bank_id, bank_name, app_name)
    VALUES (%s, %s, %s)
    ON CONFLICT (bank_id) DO NOTHING
"""

INSERT_REVIEW_SQL = """
    INSERT INTO reviews (
        review_id, bank_id, review_text, rating, review_date,
        sentiment_label, sentiment_score, identified_theme, source
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (review_id) DO NOTHING
"""


@contextmanager
def get_connection(config: DBConfig | None = None) -> Iterator[PGConnection]:
    """Context-managed Postgres connection; commits on success, rolls back on error."""
    config = config or DBConfig()
    conn = psycopg2.connect(**config.as_dsn_kwargs())
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def insert_banks(conn: PGConnection) -> None:
    """Insert the three configured banks (idempotent via ON CONFLICT DO NOTHING)."""
    rows = [
        (BANK_ID_BY_NAME[bank.display_name], bank.display_name, bank.display_name)
        for bank in BANKS
    ]
    with conn.cursor() as cursor:
        cursor.executemany(INSERT_BANK_SQL, rows)
    logger.info("Inserted/verified %d bank rows.", len(rows))


def insert_reviews(conn: PGConnection, df: pd.DataFrame) -> int:
    """
    Bulk-insert processed reviews. Expects columns:
    review_id, bank_id, review_text, rating, review_date,
    sentiment_label, sentiment_score, identified_theme, source.
    """
    records = list(
        df[
            [
                "review_id", "bank_id", "review_text", "rating", "review_date",
                "sentiment_label", "sentiment_score", "identified_theme", "source",
            ]
        ].itertuples(index=False, name=None)
    )
    with conn.cursor() as cursor:
        cursor.executemany(INSERT_REVIEW_SQL, records)
    logger.info("Inserted/verified %d review rows.", len(records))
    return len(records)


def verify_data_integrity(conn: PGConnection) -> pd.DataFrame:
    """Run the verification queries from the brief: counts, avg rating, null checks."""
    query = """
        SELECT
            b.bank_name,
            COUNT(r.review_id)                                   AS review_count,
            ROUND(AVG(r.rating)::numeric, 2)                      AS avg_rating,
            SUM(CASE WHEN r.review_text IS NULL THEN 1 ELSE 0 END) AS null_review_text,
            SUM(CASE WHEN r.rating IS NULL THEN 1 ELSE 0 END)      AS null_rating
        FROM banks b
        LEFT JOIN reviews r ON r.bank_id = b.bank_id
        GROUP BY b.bank_name
        ORDER BY b.bank_name
    """
    return pd.read_sql(query, conn)
