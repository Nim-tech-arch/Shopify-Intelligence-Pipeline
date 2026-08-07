import os
import sqlite3
import tempfile
import unittest

from shopify.db_manager import init_db, save_to_db


class DatabaseManagerContractTests(unittest.TestCase):
    def test_init_db_and_save_to_db_store_records_without_duplicates(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "shopify_intelligence.db")
            conn = init_db(db_path=db_path)
            try:
                self.assertTrue(os.path.exists(db_path))

                records = [
                    {
                        "store_url": "https://example.com",
                        "crawl_timestamp": "2026-08-07T00:00:00+00:00",
                        "product_id": "1001",
                        "product_title": "Example Product",
                        "variant_id": "2001",
                        "sku": "SKU-1",
                        "price": 19.99,
                        "discount_spread": 2.5,
                        "inventory_quantity": 10,
                        "available": True,
                    }
                ]

                inserted = save_to_db(records, db_path=db_path)
                self.assertEqual(inserted, 1)

                inserted_again = save_to_db(records, db_path=db_path)
                self.assertEqual(inserted_again, 0)

                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM product_snapshots")
                self.assertEqual(cursor.fetchone()[0], 1)
            finally:
                conn.close()


if __name__ == "__main__":
    unittest.main()
