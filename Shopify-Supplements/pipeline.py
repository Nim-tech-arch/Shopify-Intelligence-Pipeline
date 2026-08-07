"""Orchestration entry point for the Shopify intelligence pipeline."""

from __future__ import annotations

import asyncio
import json
from typing import Any

import httpx

from shopify.analytics import get_market_insights
from shopify.db_manager import save_to_db

from .config import MAX_CONCURRENCY, STOREFRONT_TOKENS, TARGET_STORES
from .engine import fetch_catalog
from .graphql_client import fetch_storefront_graphql
from .normalizer import normalize_product_data

OUTPUT_FILENAME = "shopify_supplement_intelligence.json"


async def run_pipeline(stores: list[str] | None = None) -> list[dict[str, Any]]:
    """Fetch each Shopify store catalog and return normalized product records."""
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
    master_dataset: list[dict[str, Any]] = []
    async with httpx.AsyncClient(follow_redirects=True, http2=True) as client:
        for store_url in stores or TARGET_STORES:
            clean_store_url = store_url.rstrip("/")
            token = STOREFRONT_TOKENS.get(clean_store_url)

            if token:
                print(f"[*] Attempting Storefront GraphQL for: {clean_store_url}")
                gql_payload = await fetch_storefront_graphql(clean_store_url, token, client)
                if gql_payload is not None:
                    normalized = normalize_product_data(clean_store_url, gql_payload)
                    if normalized:
                        master_dataset.extend(normalized)
                        continue

                    print(f"[-] {clean_store_url}: Storefront GraphQL returned no normalized products; falling back to public JSON")
                else:
                    print(f"[-] {clean_store_url}: Storefront GraphQL failed or returned no payload; falling back to public JSON")

            _, raw_products = await fetch_catalog(client, clean_store_url, semaphore)
            if raw_products:
                normalized = normalize_product_data(clean_store_url, raw_products)
                master_dataset.extend(normalized)

    return master_dataset


async def main() -> None:
    master_dataset = await run_pipeline()

    with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
        json.dump(master_dataset, f, indent=2)

    persisted = 0
    if master_dataset:
        persisted = save_to_db(master_dataset)
        print("[✔] Data persisted to database.")
        get_market_insights()

    print(f"\n[✔] Pipeline execution complete. Total normalized records: {len(master_dataset)}")
    print(f"[✔] Data saved securely to {OUTPUT_FILENAME}")
    if persisted:
        print(f"[✔] Persisted {persisted} new snapshot rows to the local SQLite database")


if __name__ == "__main__":
    asyncio.run(main())
