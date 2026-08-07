"""Asynchronous HTTP worker and semaphore manager for Shopify requests."""

from __future__ import annotations

import asyncio
import random
from typing import Any

try:
    import httpx
except ImportError:  # pragma: no cover - exercised when dependency is missing
    httpx = None

from .config import DEFAULT_HEADERS, HEADERS, RATE_LIMIT_SETTINGS, REQUEST_TIMEOUT, STOREFRONT_TOKENS
from .graphql_client import fetch_storefront_graphql


def _extract_graphql_products(payload: Any) -> list[dict[str, Any]]:
    """Convert Storefront GraphQL payloads into the product shape expected by the normalizer."""
    if not isinstance(payload, dict):
        return []

    data = payload.get("data")
    if not isinstance(data, dict):
        return []

    products = data.get("products")
    if not isinstance(products, dict):
        return []

    edges = products.get("edges")
    if not isinstance(edges, list):
        return []

    extracted_products: list[dict[str, Any]] = []
    for edge in edges:
        if not isinstance(edge, dict):
            continue

        node = edge.get("node")
        if not isinstance(node, dict):
            continue

        variants: list[dict[str, Any]] = []
        variants_payload = node.get("variants")
        if isinstance(variants_payload, dict):
            variant_edges = variants_payload.get("edges")
            if isinstance(variant_edges, list):
                for variant_edge in variant_edges:
                    if not isinstance(variant_edge, dict):
                        continue

                    variant_node = variant_edge.get("node")
                    if not isinstance(variant_node, dict):
                        continue

                    price_node = variant_node.get("price")
                    compare_price_node = variant_node.get("compareAtPrice")
                    variants.append(
                        {
                            "id": variant_node.get("id"),
                            "title": variant_node.get("title"),
                            "sku": variant_node.get("sku"),
                            "price": price_node.get("amount") if isinstance(price_node, dict) else None,
                            "compare_at_price": compare_price_node.get("amount") if isinstance(compare_price_node, dict) else None,
                            "available": variant_node.get("availableForSale"),
                            "availableForSale": variant_node.get("availableForSale"),
                            "inventory_quantity": variant_node.get("quantityAvailable"),
                            "quantityAvailable": variant_node.get("quantityAvailable"),
                        }
                    )

        extracted_products.append(
            {
                "id": node.get("id"),
                "title": node.get("title"),
                "handle": node.get("handle"),
                "vendor": node.get("vendor"),
                "product_type": node.get("productType"),
                "variants": variants,
            }
        )

    return extracted_products


async def fetch_catalog(client: Any, base_url: str, semaphore: asyncio.Semaphore) -> tuple[str, list[dict[str, Any]]]:
    """Fetch a Shopify catalog one page at a time with jitter and rate limiting."""
    async with semaphore:
        page = 1
        raw_products: list[dict[str, Any]] = []
        clean_base = base_url.rstrip("/")

        print(f"[*] Extracting catalog for: {clean_base}")

        token = STOREFRONT_TOKENS.get(clean_base)
        if token:
            try:
                print(f"[*] Attempting Storefront GraphQL for: {clean_base}")
                gql_payload = await fetch_storefront_graphql(clean_base, token, client)
                gql_products = _extract_graphql_products(gql_payload)
                if gql_products:
                    print(f"[+] {clean_base}: Storefront GraphQL returned ({len(gql_products)} products)")
                    return clean_base, gql_products

                print(f"[-] Storefront GraphQL returned no products for {clean_base}; falling back to public JSON")
            except Exception as exc:
                print(f"[!] Storefront GraphQL failed for {clean_base}: {exc}")

        while True:
            url = f"{clean_base}/collections/all/products.json?page={page}&limit=250"
            try:
                await asyncio.sleep(random.uniform(1.5, 3.5))

                response = await client.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)

                if response.status_code in (403, 404):
                    print(f"[-] Endpoint closed or blocked for {clean_base} (HTTP {response.status_code})")
                    break

                response.raise_for_status()
                data = response.json()
                products = data.get("products", [])

                if not products:
                    break

                raw_products.extend(products)
                print(f"[+] {clean_base}: Page {page} fetched ({len(products)} products)")
                page += 1
            except Exception as exc:
                print(f"[!] Network error on {clean_base} [Page {page}]: {exc}")
                break

        return clean_base, raw_products


class AsyncHttpWorker:
    """Small async wrapper around httpx with bounded concurrency."""

    def __init__(self, *, max_concurrency: int | None = None) -> None:
        self.max_concurrency = max_concurrency or RATE_LIMIT_SETTINGS["max_concurrency"]
        self.semaphore = asyncio.Semaphore(self.max_concurrency)
        self.timeout = RATE_LIMIT_SETTINGS["timeout_seconds"]

    async def fetch(self, url: str, *, headers: dict[str, str] | None = None) -> dict[str, Any]:
        if httpx is None:
            raise RuntimeError("httpx is required to run the async fetch worker")

        async with self.semaphore:
            async with httpx.AsyncClient(headers=headers or DEFAULT_HEADERS, timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                return {"url": url, "status_code": response.status_code, "text": response.text}
