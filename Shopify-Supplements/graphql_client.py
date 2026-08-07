"""GraphQL client helpers for Shopify Storefront API access."""

from __future__ import annotations

import httpx

GRAPHQL_QUERY = """{
  products(first: 50) {
    edges {
      node {
        id
        title
        handle
        vendor
        productType
        variants(first: 10) {
          edges {
            node {
              id
              title
              sku
              price {
                amount
                currencyCode
              }
              compareAtPrice {
                amount
                currencyCode
              }
              quantityAvailable
              availableForSale
            }
          }
        }
      }
    }
  }
}
"""


async def fetch_storefront_graphql(
    store_url: str,
    access_token: str,
    client: httpx.AsyncClient,
):
    """Fetch product inventory and pricing from Shopify's Storefront GraphQL API."""
    endpoint = f"{store_url.rstrip('/')}/api/2023-07/graphql.json"
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Storefront-Access-Token": access_token,
    }

    payload = {"query": GRAPHQL_QUERY}

    try:
        response = await client.post(endpoint, json=payload, headers=headers, timeout=15.0)
        if response.status_code == 200:
            return response.json()

        print(f"[-] GraphQL error on {store_url}: HTTP {response.status_code}")
        return None
    except Exception as exc:  # pragma: no cover - defensive logging path
        print(f"[!] Network error on GraphQL for {store_url}: {exc}")
        return None
