"""Orchestration entry point for the Shopify intelligence pipeline with true async concurrency."""

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

from .analytics import print_market_insights_dashboard
from .config import MAX_CONCURRENCY, STOREFRONT_TOKENS, TARGET_STORES
from .db_manager import save_to_db
from .engine import fetch_catalog
from .graphql_client import fetch_storefront_graphql
from .normalizer import normalize_product_data

logger = logging.getLogger(__name__)
OUTPUT_FILENAME = Path("shopify_supplement_intelligence.json")


async def process_store(
    store_url: str,
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
) -> List[Dict[str, Any]]:
    """Fetch and normalize catalog data for a single target store."""
    clean_url = store_url.rstrip("/")
    token = STOREFRONT_TOKENS.get(clean_url)

    if token:
        try:
            gql_payload = await fetch_storefront_graphql(clean_url, token, client)
            if gql_payload:
                normalized = normalize_product_data(clean_url, gql_payload)
                if normalized:
                    return normalized
        except Exception:
            pass

    _, raw_products = await fetch_catalog(client, clean_url, semaphore)
    if raw_products:
        return normalize_product_data(clean_url, raw_products)
    return []


async def run_pipeline(stores: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Fetch all Shopify catalogs concurrently using an async task pool."""
    target_stores = stores or TARGET_STORES
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
    master_dataset: List[Dict[str, Any]] = []

    async with httpx.AsyncClient(
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
        },
        follow_redirects=True,
    ) as client:
        # Launch ingestion for all stores concurrently using asyncio.gather
        tasks = [process_store(url, client, semaphore) for url in target_stores]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for res in results:
            if isinstance(res, list):
                master_dataset.extend(res)

    return master_dataset


async def main() -> None:
    """Pipeline orchestrator execution entrypoint."""
    master_dataset = await run_pipeline()

    with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
        json.dump(master_dataset, f, indent=2)

    persisted = 0
    if master_dataset:
        persisted = save_to_db(master_dataset)
        print("[✔] Data persisted to database.")
        print_market_insights_dashboard()

    print(f"\n[✔] Pipeline execution complete. Total normalized records: {len(master_dataset)}")
    print(f"[✔] Data saved securely to {OUTPUT_FILENAME}")
    if persisted:
        print(f"[✔] Persisted {persisted} new snapshot rows to the local SQLite database")


if __name__ == "__main__":
    asyncio.run(main())