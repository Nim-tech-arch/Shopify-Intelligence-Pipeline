import asyncio
import unittest
from unittest import mock

from shopify.engine import fetch_catalog


class FakeResponse:
    def __init__(self, payload, *, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self):
        return self._payload


class FakeAsyncClient:
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    async def get(self, url, *, headers=None, timeout=None):
        self.calls.append((url, headers, timeout))
        if not self._responses:
            return FakeResponse({"products": []})
        return self._responses.pop(0)


class EngineContractTests(unittest.TestCase):
    def test_fetch_catalog_paginate_and_collect_products(self) -> None:
        client = FakeAsyncClient([
            FakeResponse({"products": [{"id": 1}]}),
            FakeResponse({"products": [{"id": 2}]}),
            FakeResponse({"products": []}),
        ])
        semaphore = asyncio.Semaphore(1)

        base_url, products = asyncio.run(fetch_catalog(client, "https://store.example.com/", semaphore))

        self.assertEqual(base_url, "https://store.example.com")
        self.assertEqual([product["id"] for product in products], [1, 2])
        self.assertEqual(len(client.calls), 3)
        self.assertIn("page=1", client.calls[0][0])
        self.assertIn("page=2", client.calls[1][0])
        self.assertIn("page=3", client.calls[2][0])

    def test_fetch_catalog_uses_storefront_graphql_when_token_is_configured(self) -> None:
        class GraphQLAwareClient(FakeAsyncClient):
            def __init__(self):
                super().__init__([])
                self.graphql_calls = []

            async def post(self, url, *, json=None, headers=None, timeout=None):
                self.graphql_calls.append((url, json, headers, timeout))
                return FakeResponse({"data": {"products": {"edges": [{"node": {"id": "gid://shopify/Product/1", "title": "Test Product", "handle": "test-product", "vendor": "Test", "productType": "Supplement", "variants": {"edges": [{"node": {"id": "gid://shopify/ProductVariant/1", "title": "Default", "sku": "SKU-1", "price": {"amount": "19.99", "currencyCode": "USD"}, "compareAtPrice": {"amount": "24.99", "currencyCode": "USD"}, "quantityAvailable": 5, "availableForSale": True}}]}}}]}}})

        client = GraphQLAwareClient()
        semaphore = asyncio.Semaphore(1)

        with mock.patch("shopify.engine.STOREFRONT_TOKENS", {"https://store.example.com": "public-token"}):
            base_url, products = asyncio.run(fetch_catalog(client, "https://store.example.com/", semaphore))

        self.assertEqual(base_url, "https://store.example.com")
        self.assertEqual(products[0]["title"], "Test Product")
        self.assertEqual(products[0]["variants"][0]["price"], "19.99")
        self.assertEqual(len(client.graphql_calls), 1)
        self.assertEqual(len(client.calls), 0)


if __name__ == "__main__":
    unittest.main()
