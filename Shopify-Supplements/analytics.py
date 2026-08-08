"""Analytics helpers for inspecting discounted products and inventory trends."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

try:
    import pandas as pd
except ImportError:  # pragma: no cover - exercised when dependency is missing
    pd = None

from .db_manager import DEFAULT_DB_PATH


def _format_table(headers: list[str], rows: list[tuple[Any, ...]]) -> str:
    """Render a simple text table when pandas is unavailable."""
    if not rows:
        return "No data available"

    widths = [len(header) for header in headers]
    for row in rows:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], len(str(value)))

    header_line = " | ".join(header.ljust(widths[index]) for index, header in enumerate(headers))
    separator = "-+-".join("-" * width for width in widths)
    body_lines = [" | ".join(str(value).ljust(widths[index]) for index, value in enumerate(row)) for row in rows]
    return "\n".join([header_line, separator, *body_lines])


def get_market_insights(db_path: str | Path | None = None) -> dict[str, list[dict[str, Any]]]:
    """Return discount and inventory analytics from the SQLite snapshot table."""
    resolved_path = Path(db_path) if db_path is not None else DEFAULT_DB_PATH
    conn = sqlite3.connect(resolved_path)

    try:
        top_discounted_query = """
            WITH RankedDiscounts AS (
                SELECT
                    store_url,
                    product_title,
                    price,
                    ROUND(discount_spread, 2) AS discount_spread,
                    ROW_NUMBER() OVER (
                        PARTITION BY product_title
                        ORDER BY discount_spread DESC, price DESC
                    ) AS rn
                FROM product_snapshots
                WHERE discount_spread > 0
            )
            SELECT store_url, product_title, price, discount_spread
            FROM RankedDiscounts
            WHERE rn = 1
            ORDER BY discount_spread DESC, price DESC
            LIMIT 10
        """
        top_discounted_rows = conn.execute(top_discounted_query).fetchall()

        inventory_query = """
            SELECT store_url, COUNT(*) AS snapshot_count,
                   SUM(CASE
                           WHEN COALESCE(inventory_quantity, 0) > 0 THEN 1
                           WHEN COALESCE(available, 0) = 1 THEN 1
                           ELSE 0
                       END) AS in_stock_count,
                   AVG(CASE
                           WHEN COALESCE(inventory_quantity, 0) > 0 THEN inventory_quantity
                           WHEN COALESCE(available, 0) = 1 THEN 1
                           ELSE 0
                       END) AS avg_inventory
            FROM product_snapshots
            GROUP BY store_url
            ORDER BY avg_inventory DESC, snapshot_count DESC
        """
        inventory_rows = conn.execute(inventory_query).fetchall()
    finally:
        conn.close()

    top_discounted_products = [
        {
            "store_url": row[0],
            "product_title": row[1],
            "price": row[2],
            "discount_spread": round(float(row[3]), 2) if row[3] is not None else 0.0,
        }
        for row in top_discounted_rows
    ]

    inventory_trends = [
        {
            "store_url": row[0],
            "snapshot_count": int(row[1]),
            "in_stock_count": int(row[2]),
            "avg_inventory": round(float(row[3]), 2),
            "availability_based_in_stock_count": int(row[2]),
            "avg_availability_score": round(float(row[3]), 2),
        }
        for row in inventory_rows
    ]

    print("\n--- Top 10 Heaviest Discounted SKUs ---")
    if pd is not None:
        top_discounted_df = pd.DataFrame(
            top_discounted_rows,
            columns=["store_url", "product_title", "price", "discount_spread"],
        )
        print(top_discounted_df.to_string(index=False))
    else:
        print(_format_table(["store_url", "product_title", "price", "discount_spread"], top_discounted_rows))

    print("\n--- Store Inventory Trends (availability-based) ---")
    inventory_headers = ["store_url", "snapshot_count", "availability_based_in_stock_count", "avg_availability_score"]
    if pd is not None:
        inventory_df = pd.DataFrame(
            inventory_rows,
            columns=["store_url", "snapshot_count", "in_stock_count", "avg_inventory"],
        )
        inventory_df.columns = inventory_headers
        print(inventory_df.to_string(index=False))
    else:
        print(_format_table(inventory_headers, inventory_rows))

    return {
        "top_discounted_products": top_discounted_products,
        "inventory_trends": inventory_trends,
    }
