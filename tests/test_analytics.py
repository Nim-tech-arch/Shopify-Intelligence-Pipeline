import io
import os
import sqlite3
import tempfile
import unittest
from contextlib import redirect_stdout

from shopify.analytics import get_market_insights


class AnalyticsContractTests(unittest.TestCase):
    def test_get_market_insights_reports_discounted_products_and_inventory_trends(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "shopify_intelligence.db")
            conn = sqlite3.connect(db_path)
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    CREATE TABLE product_snapshots (
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
                cursor.executemany(
                    """
                    INSERT INTO product_snapshots (
                        store_url, crawl_timestamp, product_id, product_title, variant_id,
                        sku, price, discount_spread, inventory_quantity, available
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    [
                        (
                            "https://store-a.com",
                            "2026-08-07T00:00:00+00:00",
                            "1001",
                            "Premium Jacket",
                            "2001",
                            "SKU-1",
                            89.99,
                            25.0,
                            12,
                            True,
                        ),
                        (
                            "https://store-a.com",
                            "2026-08-07T00:00:01+00:00",
                            "1002",
                            "Classic Tee",
                            "2002",
                            "SKU-2",
                            24.0,
                            5.0,
                            4,
                            True,
                        ),
                        (
                            "https://store-b.com",
                            "2026-08-07T00:00:02+00:00",
                            "1003",
                            "Winter Boots",
                            "2003",
                            "SKU-3",
                            120.0,
                            30.0,
                            0,
                            False,
                        ),
                    ],
                )
                conn.commit()
            finally:
                conn.close()

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                insights = get_market_insights(db_path=db_path)

            output = stdout.getvalue()
            self.assertIn("Top 10 Heaviest Discounted SKUs", output)
            self.assertIn("Store Inventory Trends", output)
            self.assertIn("availability-based", output)
            self.assertEqual(insights["top_discounted_products"][0]["product_title"], "Winter Boots")
            self.assertEqual(insights["inventory_trends"][0]["store_url"], "https://store-a.com")
            self.assertEqual(insights["inventory_trends"][0]["availability_based_in_stock_count"], 2)

    def test_get_market_insights_uses_availability_when_inventory_quantity_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "shopify_intelligence.db")
            conn = sqlite3.connect(db_path)
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    CREATE TABLE product_snapshots (
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
                cursor.executemany(
                    """
                    INSERT INTO product_snapshots (
                        store_url, crawl_timestamp, product_id, product_title, variant_id,
                        sku, price, discount_spread, inventory_quantity, available
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    [
                        (
                            "https://store-c.com",
                            "2026-08-07T00:00:00+00:00",
                            "3001",
                            "Inventoryless Product",
                            "4001",
                            "SKU-C1",
                            19.99,
                            0.0,
                            None,
                            True,
                        ),
                        (
                            "https://store-c.com",
                            "2026-08-07T00:00:01+00:00",
                            "3002",
                            "Inventoryless Product 2",
                            "4002",
                            "SKU-C2",
                            29.99,
                            0.0,
                            0,
                            True,
                        ),
                        (
                            "https://store-d.com",
                            "2026-08-07T00:00:02+00:00",
                            "3003",
                            "Unavailable Product",
                            "4003",
                            "SKU-D1",
                            39.99,
                            0.0,
                            0,
                            False,
                        ),
                    ],
                )
                conn.commit()
            finally:
                conn.close()

            insights = get_market_insights(db_path=db_path)

            self.assertEqual(insights["inventory_trends"][0]["store_url"], "https://store-c.com")
            self.assertEqual(insights["inventory_trends"][0]["in_stock_count"], 2)
            self.assertEqual(insights["inventory_trends"][0]["avg_inventory"], 1.0)

    def test_get_market_insights_rounds_discount_spread_to_two_decimals(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "shopify_intelligence.db")
            conn = sqlite3.connect(db_path)
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    CREATE TABLE product_snapshots (
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
                    INSERT INTO product_snapshots (
                        store_url, crawl_timestamp, product_id, product_title, variant_id,
                        sku, price, discount_spread, inventory_quantity, available
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        "https://store-x.com",
                        "2026-08-07T00:00:00+00:00",
                        "9001",
                        "Rounded Discount SKU",
                        "7001",
                        "SKU-X",
                        29.99,
                        29.999999999999993,
                        3,
                        True,
                    ),
                )
                conn.commit()
            finally:
                conn.close()

            insights = get_market_insights(db_path=db_path)

            self.assertEqual(insights["top_discounted_products"][0]["discount_spread"], 30.0)


if __name__ == "__main__":
    unittest.main()
