import unittest

from shopify.normalizer import normalize_product_data


class NormalizerContractTests(unittest.TestCase):
    def test_normalize_product_data_flattens_variants_and_metrics(self) -> None:
        raw_products = [
            {
                "id": 101,
                "title": "Example Product",
                "handle": "example-product",
                "vendor": "Example Vendor",
                "product_type": "Accessory",
                "variants": [
                    {
                        "id": 1001,
                        "title": "Default Title",
                        "sku": "SKU-1",
                        "price": "12.50",
                        "compare_at_price": "15.00",
                        "available": True,
                        "inventory_quantity": 3,
                    },
                    {
                        "id": 1002,
                        "title": "Second Option",
                        "sku": "SKU-2",
                        "price": "10.00",
                        "compare_at_price": None,
                        "available": False,
                        "inventory_quantity": 0,
                    },
                ],
            }
        ]

        records = normalize_product_data("https://store.example.com", raw_products)

        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["store_url"], "https://store.example.com")
        self.assertEqual(records[0]["product_id"], 101)
        self.assertEqual(records[0]["sku"], "SKU-1")
        self.assertEqual(records[0]["discount_spread"], 2.5)
        self.assertEqual(records[0]["inventory_quantity"], 3)
        self.assertTrue(records[0]["available"])
        self.assertEqual(records[1]["compare_at_price"], 10.0)
        self.assertEqual(records[1]["discount_spread"], 0.0)
        self.assertFalse(records[1]["available"])
        self.assertIn("crawl_timestamp", records[0])

    def test_normalize_product_data_handles_missing_variants_and_null_fields(self) -> None:
        raw_products = [
            {
                "id": 202,
                "title": "No Variant Product",
                "handle": "no-variant-product",
                "vendor": "Example Vendor",
                "product_type": "Apparel",
                "variants": None,
            },
            {
                "id": 303,
                "title": "Nullable Inventory Product",
                "handle": "nullable-inventory-product",
                "vendor": "Example Vendor",
                "product_type": "Apparel",
                "variants": [
                    {
                        "id": 3001,
                        "title": "Default Title",
                        "sku": None,
                        "price": None,
                        "compare_at_price": None,
                        "available": None,
                        "inventory_quantity": None,
                    }
                ],
            },
        ]

        records = normalize_product_data("https://store.example.com", raw_products)

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["product_id"], 303)
        self.assertEqual(records[0]["sku"], None)
        self.assertEqual(records[0]["price"], 0.0)
        self.assertEqual(records[0]["compare_at_price"], 0.0)
        self.assertEqual(records[0]["discount_spread"], 0.0)
        self.assertEqual(records[0]["inventory_quantity"], 0)
        self.assertFalse(records[0]["available"])

    def test_normalize_product_data_extracts_products_from_nested_response(self) -> None:
        raw_products = {
            "products": [
                {
                    "id": 404,
                    "title": "Nested Product",
                    "handle": "nested-product",
                    "vendor": "Example Vendor",
                    "product_type": "Accessory",
                    "variants": [
                        {
                            "id": 4001,
                            "title": "Default Title",
                            "sku": "SKU-404",
                            "price": "20.00",
                            "compare_at_price": "25.00",
                            "available": True,
                            "inventory_quantity": 10,
                        }
                    ],
                }
            ]
        }

        records = normalize_product_data("https://store.example.com", raw_products)

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["product_id"], 404)
        self.assertEqual(records[0]["sku"], "SKU-404")
        self.assertEqual(records[0]["inventory_quantity"], 10)

    def test_normalize_product_data_uses_graphql_inventory_and_availability_fields(self) -> None:
        raw_products = [
            {
                "id": 505,
                "title": "GraphQL Product",
                "handle": "graphql-product",
                "vendor": "Example Vendor",
                "product_type": "Accessory",
                "variants": [
                    {
                        "id": 5001,
                        "title": "Default Title",
                        "sku": "SKU-505",
                        "price": "19.99",
                        "compare_at_price": "24.99",
                        "availableForSale": True,
                        "quantityAvailable": 8,
                    }
                ],
            }
        ]

        records = normalize_product_data("https://store.example.com", raw_products)

        self.assertEqual(len(records), 1)
        self.assertTrue(records[0]["available"])
        self.assertEqual(records[0]["inventory_quantity"], 8)


if __name__ == "__main__":
    unittest.main()
