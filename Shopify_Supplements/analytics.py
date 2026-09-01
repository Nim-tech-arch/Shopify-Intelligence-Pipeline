"""Analytics and terminal reporting helpers for Shopify competitor insights."""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .db_manager import DEFAULT_DB_PATH

logger = logging.getLogger(__name__)


def _format_table(headers: List[str], rows: List[Tuple[Any, ...]]) -> str:
    """Renders a formatted ASCII text table."""
    if not rows:
        return "No data available"

    widths = [len(header) for header in headers]
    for row in rows:
        for idx, val in enumerate(row):
            widths[idx] = max(widths[idx], len(str(val)))

    header_line = " | ".join(header.ljust(widths[i]) for i, header in enumerate(headers))
    separator = "-+-".join("-" * width for width in widths)
    body_lines = [
        " | ".join(str(val).ljust(widths[i]) for i, val in enumerate(row))
        for row in rows
    ]
    return "\n".join([header_line, separator, *body_lines])


def fetch_latest_market_insights(
    db_path: str | Path | None = None,
) -> Dict[str, List[Dict[str, Any]]]:
    """Queries SQLite database for top discounts and inventory availability metrics 
    strictly bounded to the most recent crawl snapshot per store.
    """
    resolved_path = Path(db_path) if db_path is not None else DEFAULT_DB_PATH
    if not resolved_path.exists():
        logger.warning("Database file does not exist at %s", resolved_path)
        return {"top_discounted_products": [], "inventory_trends": []}

    conn = sqlite3.connect(resolved_path)
    try:
        # 1. Top 10 Discounted SKUs from the latest crawl iteration
        top_discounted_query = """
        WITH LatestSnapshots AS (
            SELECT *,
                   ROW_NUMBER() OVER (
                       PARTITION BY store_url, variant_id 
                       ORDER BY crawl_timestamp DESC
                   ) as recency_rank
            FROM product_snapshots
        ),
        RankedDiscounts AS (
            SELECT store_url, product_title, price, round(discount_spread, 2) as discount_spread,
                   ROW_NUMBER() OVER (
                       PARTITION BY product_title 
                       ORDER BY discount_spread DESC, price DESC
                   ) as rn
            FROM LatestSnapshots
            WHERE recency_rank = 1 AND discount_spread > 0
        )
        SELECT store_url, product_title, price, discount_spread
        FROM RankedDiscounts
        WHERE rn = 1
        ORDER BY discount_spread DESC, price DESC
        LIMIT 10
        """

        # 2. Store-level In-Stock Rate (%) from the latest crawl iteration
        inventory_query = """
        WITH LatestSnapshots AS (
            SELECT *,
                   ROW_NUMBER() OVER (
                       PARTITION BY store_url, variant_id 
                       ORDER BY crawl_timestamp DESC
                   ) as recency_rank
            FROM product_snapshots
        )
        SELECT 
            store_url,
            COUNT(*) AS total_skus,
            SUM(CASE WHEN available = 1 THEN 1 ELSE 0 END) AS in_stock_skus,
            ROUND(AVG(CASE WHEN available = 1 THEN 1.0 ELSE 0.0 END) * 100, 2) AS availability_pct
        FROM LatestSnapshots
        WHERE recency_rank = 1
        GROUP BY store_url
        ORDER BY availability_pct DESC, total_skus DESC
        """

        top_discounted_rows = conn.execute(top_discounted_query).fetchall()
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
            "total_skus": int(row[1]),
            "in_stock_skus": int(row[2]),
            "availability_pct": float(row[3]),
        }
        for row in inventory_rows
    ]

    return {
        "top_discounted_products": top_discounted_products,
        "inventory_trends": inventory_trends,
    }


def print_market_insights_dashboard(db_path: str | Path | None = None) -> None:
    """CLI Formatter method to print analytics cleanly to standard output."""
    insights = fetch_latest_market_insights(db_path)

    print("\n=======================================================")
    print("      SHOPIFY INTELLIGENCE: LATEST MARKET INSIGHTS     ")
    print("=======================================================")

    print("\n--- Top 10 Heaviest Discounted SKUs ---")
    disc_data = [
        (p["store_url"], p["product_title"][:30], p["price"], p["discount_spread"])
        for p in insights["top_discounted_products"]
    ]
    print(_format_table(["Store URL", "Product Title", "Price ($)", "Discount ($)"], disc_data))

    print("\n--- Store Inventory Availability Trends (%) ---")
    inv_data = [
        (i["store_url"], i["total_skus"], i["in_stock_skus"], f"{i['availability_pct']}%")
        for i in insights["inventory_trends"]
    ]
    print(_format_table(["Store URL", "Total SKUs", "In-Stock SKUs", "Availability Rate"], inv_data))