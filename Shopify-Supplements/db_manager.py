"""SQLite persistence helpers for normalized Shopify product snapshots."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "shopify_intelligence.db"


def init_db(db_path: str | Path | None = None) -> sqlite3.Connection:
    """Create the SQLite database and schema if they do not already exist."""
    resolved_path = Path(db_path) if db_path is not None else DEFAULT_DB_PATH
    resolved_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(resolved_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS product_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            store_url TEXT NOT NULL,
            crawl_timestamp TEXT NOT NULL,
            product_id TEXT NOT NULL,
            product_title TEXT,
            variant_id TEXT,
            sku TEXT,
            price REAL,
            discount_spread REAL,
            inventory_quantity INTEGER,
            available BOOLEAN,
            UNIQUE(store_url, crawl_timestamp, product_id, variant_id)
        )
        """
    )
    conn.commit()
    return conn


def save_to_db(records: list[dict[str, Any]], db_path: str | Path | None = None) -> int:
    """Persist records into SQLite and skip duplicates based on a unique composite key."""
    if not records:
        return 0

    conn = init_db(db_path)
    cursor = conn.cursor()
    inserted_count = 0

    for record in records:
        try:
            cursor.execute(
                """
                INSERT OR IGNORE INTO product_snapshots (
                    store_url, crawl_timestamp, product_id, product_title, variant_id,
                    sku, price, discount_spread, inventory_quantity, available
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.get("store_url"),
                    record.get("crawl_timestamp"),
                    record.get("product_id"),
                    record.get("product_title"),
                    record.get("variant_id"),
                    record.get("sku"),
                    record.get("price"),
                    record.get("discount_spread"),
                    record.get("inventory_quantity"),
                    bool(record.get("available", False)),
                ),
            )
            if cursor.rowcount > 0:
                inserted_count += 1
        except sqlite3.Error:
            continue

    conn.commit()
    conn.close()
    return inserted_count
