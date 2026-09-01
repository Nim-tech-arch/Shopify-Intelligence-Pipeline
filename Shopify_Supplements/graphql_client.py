"""GraphQL client helpers for Shopify Storefront API access with cursor pagination."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)

PAGINATED_GRAPHQL_QUERY = """
query GetStorefrontCatalog($productCursor: String) {
  products(first: 250, after: $productCursor) {
    pageInfo {
      hasNextPage
      endCursor
    }
    edges {
      node {
        id
        title
        handle
        vendor
        productType
        variants(first: 100) {
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
    api_version: str = "2024-07",
) -> Optional[Dict[str, Any]]:
    """Fetch complete product inventory and pricing from Shopify's Storefront GraphQL API.
    
    Handles cursor pagination across all product pages.
    """
    endpoint = f"{store_url.rstrip('/')}/api/{api_version}/graphql.json"
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Storefront-Access-Token": access_token,
    }

    all_product_edges: List[Dict[str, Any]] = []
    has_next_page = True
    cursor: Optional[str] = None

    try:
        while has_next_page:
            variables = {"productCursor": cursor}
            payload = {
                "query": PAGINATED_GRAPHQL_QUERY,
                "variables": variables,
            }

            response = await client.post(endpoint, json=payload, headers=headers, timeout=15.0)

            if response.status_code != 200:
                logger.error("GraphQL request failed for %s with HTTP status %d", store_url, response.status_code)
                return None

            json_body = response.json()

            # Handle GraphQL top-level errors (HTTP 200 with error body)
            if "errors" in json_body:
                logger.error("GraphQL query returned errors for %s: %s", store_url, json_body["errors"])
                return None

            data = json_body.get("data", {}).get("products", {})
            edges = data.get("edges", [])
            page_info = data.get("pageInfo", {})

            all_product_edges.extend(edges)

            has_next_page = page_info.get("hasNextPage", False)
            cursor = page_info.get("endCursor")

            if not has_next_page or not cursor:
                break

        # Reconstruct synthetic single GraphQL payload for normalizer compatibility
        return {
            "data": {
                "products": {
                    "edges": all_product_edges
                }
            }
        }

    except Exception as exc:
        logger.error("Network or parsing error on GraphQL endpoint for %s: %s", store_url, exc)
        return None