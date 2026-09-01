"""SQLite persistence module for normalized Shopify product historical snapshots."""

from __future__ import annotations

import logging
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Tuple

logger = logging.getLogger(__name__)

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "shopify_intelligence.db"


@contextmanager
def get_db_connection(db_path: Path) -> Generator[sqlite3.Connection, None, None]:
    """Context manager for managing SQLite connections and transactions safely."""
    conn = sqlite3.connect(db_path, timeout=30.0)
    # Enable Write-Ahead Logging (WAL) for significantly higher concurrent read/write throughput
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    try:
        yield conn
        conn.commit()
    except Exception as exc:
        conn.rollback()
        logger.error("Database transaction failed. Rolled back. Error: %s", exc)
        raise
    finally:
        conn.close()


def init_db(db_path: str | Path | None = None) -> Path:
    """Initializes SQLite database schema for append-only historical snapshot tracking."""
    resolved_path = Path(db_path) if db_path is not None else DEFAULT_DB_PATH
    resolved_path.parent.mkdir(parents=True, exist_ok=True)

    with get_db_connection(resolved_path) as conn:
        cursor = conn.cursor()
        
        # Schema optimized for append-only historical logs
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS product_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                store_url TEXT NOT NULL,
                crawl_timestamp TEXT NOT NULL,
                product_id TEXT NOT NULL,
                product_title TEXT,
                product_handle TEXT,
                variant_id TEXT NOT NULL,
                sku TEXT,
                currency TEXT DEFAULT 'USD',
                price REAL,
                compare_at_price REAL,
                discount_spread REAL,
                inventory_quantity INTEGER,
                available BOOLEAN NOT NULL
            )
            """
        )

        # Composite index to accelerate Silver-layer temporal window queries
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_snapshots_store_variant_time
            ON product_snapshots(store_url, variant_id, crawl_timestamp DESC)
            """
        )
        
        # Deduplication index enforcing uniqueness *per snapshot execution*
        cursor.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_dedup_run_snapshot
            ON product_snapshots(store_url, product_id, variant_id, crawl_timestamp)
            """
        )

    return resolved_path


def _extract_tuple(record: Dict[str, Any]) -> Tuple[Any, ...]:
    """Extracts tuple formatted for SQLite parameter binding."""
    return (
        record.get("store_url"),
        record.get("crawl_timestamp"),
        record.get("product_id"),
        record.get("product_title"),
        record.get("product_handle"),
        str(record.get("variant_id") or ""),
        record.get("sku"),
        record.get("currency", "USD"),
        record.get("price"),
        record.get("compare_at_price"),
        record.get("discount_spread"),
        record.get("inventory_quantity", 0),
        1 if record.get("available") else 0,
    )


def save_to_db(records: List[Dict[str, Any]], db_path: str | Path | None = None) -> int:
    """Persists snapshot records into SQLite using high-performance batch insert statements."""
    if not records:
        return 0

    resolved_path = init_db(db_path)

    # In-memory deduplication within the current batch
    seen_identities = set()
    unique_records: List[Dict[str, Any]] = []

    for r in records:
        key = (r.get("store_url"), r.get("product_id"), r.get("variant_id"), r.get("crawl_timestamp"))
        if key not in seen_identities:
            seen_identities.add(key)
            unique_records.append(r)

    rows_to_insert = [_extract_tuple(r) for r in unique_records]

    query = """
    INSERT OR IGNORE INTO product_snapshots (
        store_url, crawl_timestamp, product_id, product_title, product_handle,
        variant_id, sku, currency, price, compare_at_price, discount_spread,
        inventory_quantity, available
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    with get_db_connection(resolved_path) as conn:
        cursor = conn.cursor()
        cursor.executemany(query, rows_to_insert)
        inserted_count = cursor.rowcount

    logger.info("Successfully persisted %d snapshot records into SQLite", inserted_count)
    return inserted_count