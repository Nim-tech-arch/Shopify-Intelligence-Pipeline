import unittest

from shopify import config


class ConfigContractTests(unittest.TestCase):
    def test_seed_and_header_defaults_match_phase_two_contract(self) -> None:
        self.assertEqual(
            config.TARGET_STORES,
            [
                "https://www.transparentlabs.com",
                "https://kaged.com",
                "https://ghostlifestyle.com",
                "https://www.cellucor.com",
            ],
        )
        self.assertIn("User-Agent", config.HEADERS)
        self.assertEqual(config.REQUEST_TIMEOUT, 12.0)
        self.assertEqual(config.MAX_CONCURRENCY, 2)
        self.assertEqual(config.STOREFRONT_TOKENS["https://www.transparentlabs.com"], "")
        self.assertIn("https://www.cellucor.com", config.STOREFRONT_TOKENS)


if __name__ == "__main__":
    unittest.main()
