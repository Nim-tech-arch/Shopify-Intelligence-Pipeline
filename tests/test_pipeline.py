import asyncio
import unittest
from unittest import mock

from shopify.pipeline import run_pipeline


class DummyAsyncClient:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


class PipelineContractTests(unittest.TestCase):
    def test_run_pipeline_uses_storefront_graphql_when_token_is_configured(self) -> None:
        async def fake_fetch_storefront_graphql(store_url, token, client):
            self.assertEqual(store_url, "https://store.example.com")
            self.assertEqual(token, "public-token")
            return {
                "data": {
                    "products": {
                        "edges": [
                            {
                                "node": {
                                    "id": "gid://shopify/Product/1",
                                    "title": "GraphQL Product",
                                    "handle": "graphql-product",
                                    "vendor": "Example Vendor",
                                    "productType": "Supplement",
                                    "variants": {
                                        "edges": [
                                            {
                                                "node": {
                                                    "id": "gid://shopify/ProductVariant/1",
                                                    "title": "Default",
                                                    "sku": "SKU-1",
                                                    "price": {"amount": "19.99", "currencyCode": "USD"},
                                                    "compareAtPrice": {"amount": "24.99", "currencyCode": "USD"},
                                                    "quantityAvailable": 5,
                                                    "availableForSale": True,
                                                }
                                            }
                                        ]
                                    },
                                }
                            }
                        ]
                    }
                }
            }

        async def fake_fetch_catalog(*args, **kwargs):
            self.fail("pipeline should use storefront GraphQL before falling back to public fetches")

        with mock.patch("shopify.pipeline.httpx.AsyncClient", return_value=DummyAsyncClient()), \
             mock.patch("shopify.pipeline.fetch_storefront_graphql", side_effect=fake_fetch_storefront_graphql), \
             mock.patch("shopify.pipeline.fetch_catalog", side_effect=fake_fetch_catalog), \
             mock.patch("shopify.pipeline.STOREFRONT_TOKENS", {"https://store.example.com": "public-token"}):
            records = asyncio.run(run_pipeline(["https://store.example.com/"]))

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["product_title"], "GraphQL Product")
        self.assertEqual(records[0]["price"], 19.99)


if __name__ == "__main__":
    unittest.main()
