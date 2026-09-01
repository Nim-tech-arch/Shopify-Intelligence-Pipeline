import unittest

from shopify import config


class ConfigContractTests(unittest.TestCase):
    def test_target_stores_is_a_non_empty_list_of_https_urls(self) -> None:
        self.assertIsInstance(config.TARGET_STORES, list)
        self.assertGreater(len(config.TARGET_STORES), 0)
        for store_url in config.TARGET_STORES:
            self.assertTrue(store_url.startswith("https://"), store_url)
            self.assertFalse(store_url.endswith("/"), store_url)

    def test_target_stores_contains_no_duplicates(self) -> None:
        self.assertEqual(len(config.TARGET_STORES), len(set(config.TARGET_STORES)))

    def test_target_stores_includes_original_core_supplement_set(self) -> None:
        for expected_url in [
            "https://www.transparentlabs.com",
            "https://kaged.com",
            "https://ghostlifestyle.com",
            "https://www.cellucor.com",
        ]:
            self.assertIn(expected_url, config.TARGET_STORES)

    def test_target_seeds_alias_matches_target_stores(self) -> None:
        self.assertEqual(config.TARGET_SEEDS, config.TARGET_STORES)

    def test_every_target_store_has_a_storefront_token_entry(self) -> None:
        for store_url in config.TARGET_STORES:
            self.assertIn(store_url, config.STOREFRONT_TOKENS)
            self.assertEqual(config.STOREFRONT_TOKENS[store_url], "")

    def test_header_and_rate_limit_contract(self) -> None:
        self.assertIn("User-Agent", config.HEADERS)
        self.assertEqual(config.DEFAULT_HEADERS, config.HEADERS)
        self.assertEqual(config.REQUEST_TIMEOUT, 12.0)
        self.assertEqual(config.MAX_CONCURRENCY, 2)
        self.assertEqual(config.RATE_LIMIT_SETTINGS["max_concurrency"], config.MAX_CONCURRENCY)
        self.assertEqual(config.RATE_LIMIT_SETTINGS["timeout_seconds"], config.REQUEST_TIMEOUT)


if __name__ == "__main__":
    unittest.main()
