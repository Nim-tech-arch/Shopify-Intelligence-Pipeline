import asyncio
import unittest

from shopify.graphql_client import fetch_storefront_graphql


class FakeResponse:
    def __init__(self, payload, *, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def json(self):
        return self._payload


class FakeAsyncClient:
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    async def post(self, url, *, json=None, headers=None, timeout=None):
        self.calls.append((url, json, headers, timeout))
        if not self._responses:
            return FakeResponse({"data": {"products": {"edges": []}}})
        return self._responses.pop(0)


class GraphQLClientTests(unittest.TestCase):
    def test_fetch_storefront_graphql_returns_payload_for_successful_response(self) -> None:
        payload = {"data": {"products": {"edges": []}}}
        client = FakeAsyncClient([FakeResponse(payload)])

        result = asyncio.run(fetch_storefront_graphql(
            "https://store.example.com/",
            "public-token",
            client,
        ))

        self.assertEqual(result, payload)
        self.assertEqual(len(client.calls), 1)
        self.assertEqual(client.calls[0][0], "https://store.example.com/api/2023-07/graphql.json")
        self.assertEqual(client.calls[0][1]["query"], "{\n  products(first: 50) {\n    edges {\n      node {\n        id\n        title\n        handle\n        vendor\n        productType\n        variants(first: 10) {\n          edges {\n            node {\n              id\n              title\n              sku\n              price {\n                amount\n                currencyCode\n              }\n              compareAtPrice {\n                amount\n                currencyCode\n              }\n              quantityAvailable\n              availableForSale\n            }\n          }\n        }\n      }\n    }\n  }\n}\n")
        self.assertEqual(client.calls[0][2]["X-Shopify-Storefront-Access-Token"], "public-token")
        self.assertEqual(client.calls[0][3], 15.0)

    def test_fetch_storefront_graphql_returns_none_for_failed_response(self) -> None:
        client = FakeAsyncClient([FakeResponse({"errors": []}, status_code=500)])

        result = asyncio.run(fetch_storefront_graphql(
            "https://store.example.com",
            "public-token",
            client,
        ))

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
