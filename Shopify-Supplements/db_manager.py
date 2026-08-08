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
            available BOOLEAN
        )
        """
    )

    cursor.execute(
        """
        DELETE FROM product_snapshots
        WHERE id IN (
            SELECT id
            FROM (
                SELECT id,
                       ROW_NUMBER() OVER (
                           PARTITION BY store_url, product_id, COALESCE(variant_id, '')
                           ORDER BY crawl_timestamp DESC, id DESC
                       ) AS row_num
                FROM product_snapshots
            ) AS ranked
            WHERE row_num > 1
        )
        """
    )
    cursor.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_product_snapshots_identity
        ON product_snapshots(store_url, product_id, COALESCE(variant_id, ''))
        """
    )
    conn.commit()
    return conn


def _record_identity(record: dict[str, Any]) -> tuple[str, str, str]:
    """Return a stable identity for a product snapshot across pipeline runs."""
    return (
        str(record.get("store_url") or ""),
        str(record.get("product_id") or ""),
        str(record.get("variant_id") or ""),
    )


def save_to_db(records: list[dict[str, Any]], db_path: str | Path | None = None) -> int:
    """Persist records into SQLite and avoid duplicate rows across reruns."""
    if not records:
        return 0

    conn = init_db(db_path)
    cursor = conn.cursor()
    inserted_count = 0
    seen_identities: set[tuple[str, str, str]] = set()

    for record in records:
        identity = _record_identity(record)
        if identity in seen_identities:
            continue
        seen_identities.add(identity)

        try:
            existing_row = cursor.execute(
                """
                SELECT 1
                FROM product_snapshots
                WHERE store_url = ? AND product_id = ? AND COALESCE(variant_id, '') = ?
                LIMIT 1
                """,
                (identity[0], identity[1], identity[2]),
            ).fetchone()

            if existing_row is not None:
                cursor.execute(
                    """
                    UPDATE product_snapshots
                    SET crawl_timestamp = ?, product_title = ?, sku = ?, price = ?,
                        discount_spread = ?, inventory_quantity = ?, available = ?
                    WHERE store_url = ? AND product_id = ? AND COALESCE(variant_id, '') = ?
                    """,
                    (
                        record.get("crawl_timestamp"),
                        record.get("product_title"),
                        record.get("sku"),
                        record.get("price"),
                        record.get("discount_spread"),
                        record.get("inventory_quantity"),
                        bool(record.get("available", False)),
                        identity[0],
                        identity[1],
                        identity[2],
                    ),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO product_snapshots (
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
                inserted_count += 1
        except sqlite3.Error:
            continue

    conn.commit()
    conn.close()
    return inserted_count
