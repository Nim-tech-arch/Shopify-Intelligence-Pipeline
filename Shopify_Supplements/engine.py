"""Asynchronous HTTP worker and ingestion engine for Shopify storefront endpoints."""

from __future__ import annotations

import asyncio
import logging
import random
from typing import Any, List, Optional, Tuple

import httpx

from .config import settings
from .graphql_client import fetch_storefront_graphql

logger = logging.getLogger(__name__)


def _extract_graphql_products(payload: Any) -> List[dict[str, Any]]:
    """Transforms Storefront GraphQL response payload into Bronze product dictionary structure."""
    if not isinstance(payload, dict):
        return []

    edges = payload.get("data", {}).get("products", {}).get("edges", [])
    if not isinstance(edges, list):
        return []

    extracted_products: List[dict[str, Any]] = []
    for edge in edges:
        if not isinstance(edge, dict):
            continue

        node = edge.get("node")
        if not isinstance(node, dict):
            continue

        variants: List[dict[str, Any]] = []
        variant_edges = node.get("variants", {}).get("edges", [])
        if isinstance(variant_edges, list):
            for v_edge in variant_edges:
                if not isinstance(v_edge, dict):
                    continue
                v_node = v_edge.get("node", {})
                if not isinstance(v_node, dict):
                    continue

                price_node = v_node.get("price")
                compare_node = v_node.get("compareAtPrice")

                variants.append({
                    "id": v_node.get("id"),
                    "title": v_node.get("title"),
                    "sku": v_node.get("sku"),
                    "price": price_node.get("amount") if isinstance(price_node, dict) else None,
                    "compare_at_price": compare_node.get("amount") if isinstance(compare_node, dict) else None,
                    "available": v_node.get("availableForSale"),
                    "availableForSale": v_node.get("availableForSale"),
                    "inventory_quantity": v_node.get("quantityAvailable"),
                    "quantityAvailable": v_node.get("quantityAvailable"),
                })

        extracted_products.append({
            "id": node.get("id"),
            "title": node.get("title"),
            "handle": node.get("handle"),
            "vendor": node.get("vendor"),
            "product_type": node.get("productType"),
            "variants": variants,
        })

    return extracted_products


async def _execute_with_retry(
    client: httpx.AsyncClient,
    url: str,
    semaphore: asyncio.Semaphore,
    max_retries: int = 3,
) -> Optional[httpx.Response]:
    """Executes an HTTP GET request under semaphore constraint with exponential backoff retries."""
    async with semaphore:
        for attempt in range(1, max_retries + 1):
            try:
                # Add human jitter before sending request
                await asyncio.sleep(random.uniform(settings.min_jitter, settings.max_jitter))
                response = await client.get(url, timeout=settings.request_timeout)

                if response.status_code in (403, 404):
                    logger.warning("Endpoint inaccessible [%d] for URL: %s", response.status_code, url)
                    return response

                if response.status_code == 429 or response.status_code >= 500:
                    backoff = (2 ** attempt) + random.uniform(0.5, 1.5)
                    logger.warning(
                        "Rate-limited or server error [%d] on %s. Retrying in %.2fs (Attempt %d/%d)",
                        response.status_code,
                        url,
                        backoff,
                        attempt,
                        max_retries,
                    )
                    await asyncio.sleep(backoff)
                    continue

                response.raise_for_status()
                return response

            except (httpx.RequestError, httpx.HTTPStatusError) as exc:
                if attempt == max_retries:
                    logger.error("Max retries exceeded for %s. Error: %s", url, str(exc))
                    return None
                await asyncio.sleep(2 ** attempt)

    return None


async def fetch_catalog(
    client: httpx.AsyncClient,
    base_url: str,
    semaphore: asyncio.Semaphore,
    storefront_token: Optional[str] = None,
) -> Tuple[str, List[dict[str, Any]]]:
    """Fetches full product catalog for a given store, executing GraphQL or JSON fallback pagination."""
    clean_base = base_url.rstrip("/")
    logger.info("Starting ingestion for target: %s", clean_base)

    # Path 1: Storefront GraphQL (if token provided)
    if storefront_token:
        try:
            logger.info("Attempting Storefront GraphQL fetch for %s", clean_base)
            gql_payload = await fetch_storefront_graphql(clean_base, storefront_token, client)
            gql_products = _extract_graphql_products(gql_payload)
            if gql_products:
                logger.info("Successfully fetched %d products via GraphQL for %s", len(gql_products), clean_base)
                return clean_base, gql_products
            logger.warning("GraphQL returned no products for %s; falling back to REST", clean_base)
        except Exception as exc:
            logger.error("Storefront GraphQL execution failed for %s: %s", clean_base, exc)

    # Path 2: Public JSON Endpoint Pagination
    page = 1
    raw_products: List[dict[str, Any]] = []

    while True:
        url = f"{clean_base}/collections/all/products.json?page={page}&limit=250"
        response = await _execute_with_retry(client, url, semaphore)

        if not response or response.status_code in (403, 404):
            break

        try:
            data = response.json()
            products = data.get("products", [])
            if not products:
                break

            raw_products.extend(products)
            logger.info("%s: Page %d ingested (%d products)", clean_base, page, len(products))
            page += 1
        except Exception as exc:
            logger.error("Failed to parse JSON payload on page %d for %s: %s", page, clean_base, exc)
            break

    return clean_base, raw_products


class AsyncHttpWorker:
    """Async HTTP pool manager using persistent HTTP client sessions."""

    def __init__(self, max_concurrency: Optional[int] = None) -> None:
        self.max_concurrency = max_concurrency or settings.max_concurrency
        self.semaphore = asyncio.Semaphore(self.max_concurrency)
        self.client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> AsyncHttpWorker:
        self.client = httpx.AsyncClient(
            headers=settings.default_headers,
            timeout=httpx.Timeout(settings.request_timeout),
            follow_redirects=True,
        )
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self.client:
            await self.client.aclose()

    async def fetch(self, url: str) -> dict[str, Any]:
        """Fetch resource using pooled HTTP client."""
        if not self.client:
            raise RuntimeError("AsyncHttpWorker must be initialized using async context manager (`async with`)")

        async with self.semaphore:
            response = await self.client.get(url)
            response.raise_for_status()
            return {"url": url, "status_code": response.status_code, "text": response.text}