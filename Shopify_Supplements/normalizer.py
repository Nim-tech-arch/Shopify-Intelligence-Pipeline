"""Utilities to clean, flatten, and extract monetization metrics from raw Shopify payloads."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def extract_numeric_id(raw_id: Any) -> Optional[str]:
    """Normalizes Shopify GIDs (gid://shopify/Product/12345) and plain integers into clean string numeric IDs."""
    if raw_id is None:
        return None
    str_id = str(raw_id).strip()
    if "gid://" in str_id:
        match = re.search(r"/(\d+)$", str_id)
        return match.group(1) if match else str_id
    return str_id if str_id.isdigit() else str_id


def _parse_float(value: Any) -> Optional[float]:
    """Safely coerces numeric values to float, preserving None for unparseable data."""
    if value in (None, "", [], {}):
        return None
    try:
        return round(float(value), 2)
    except (TypeError, ValueError):
        return None


def _parse_int(value: Any, default: int = 0) -> int:
    """Coerces numeric values to integers, falling back safely."""
    if value in (None, "", [], {}):
        return default
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def normalize_product_data(
    store_url: str,
    raw_products: List[Dict[str, Any]] | Dict[str, Any] | None,
) -> List[Dict[str, Any]]:
    """Flattens product and variant data into a canonical flat schema (one record per variant)."""
    flat_records: List[Dict[str, Any]] = []
    crawl_timestamp = datetime.now(timezone.utc).isoformat()

    if not raw_products:
        return flat_records

    # Handle different container wrappings (single object vs list)
    productList: List[Dict[str, Any]] = []
    if isinstance(raw_products, list):
        productList = raw_products
    elif isinstance(raw_products, dict):
        productList = raw_products.get("products", [raw_products] if "title" in raw_products else [])

    for product in productList:
        if not isinstance(product, dict):
            continue

        product_id = extract_numeric_id(product.get("id"))
        title = product.get("title")
        handle = product.get("handle")
        vendor = product.get("vendor")
        product_type = product.get("product_type") or product.get("productType")

        variants = product.get("variants", [])
        if not isinstance(variants, list):
            continue

        for variant in variants:
            if not isinstance(variant, dict):
                continue

            variant_id = extract_numeric_id(variant.get("id"))
            variant_title = variant.get("title")
            sku = variant.get("sku")

            price = _parse_float(variant.get("price"))
            compare_price = _parse_float(variant.get("compare_at_price")) or price

            # Compute discount spread safely
            discount_spread = 0.0
            if price is not None and compare_price is not None:
                discount_spread = round(max(0.0, compare_price - price), 2)

            # Available indicator parsing
            available_raw = variant.get("availableForSale", variant.get("available", False))
            if isinstance(available_raw, str):
                available = available_raw.strip().lower() in {"1", "true", "yes", "on"}
            else:
                available = bool(available_raw)

            inventory_qty = _parse_int(
                variant.get("quantityAvailable", variant.get("inventory_quantity", 0)),
                default=0,
            )

            currency = variant.get("currency") or variant.get("price_currency") or "USD"

            flat_records.append({
                "store_url": store_url.rstrip("/").lower(),
                "crawl_timestamp": crawl_timestamp,
                "product_id": product_id,
                "product_title": title,
                "product_handle": handle,
                "vendor": vendor,
                "product_type": product_type,
                "variant_id": variant_id,
                "variant_title": variant_title,
                "sku": sku,
                "currency": currency,
                "price": price,
                "compare_at_price": compare_price,
                "discount_spread": discount_spread,
                "available": available,
                "inventory_quantity": inventory_qty,
            })

    return flat_records


def normalize_metrics(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Normalizes HTTP performance and operational payload metadata."""
    return {
        "metrics": {
            "url": payload.get("url"),
            "status_code": payload.get("status_code"),
            "content_length": len(payload.get("text", "") or ""),
        },
        "monetization": {
            "revenue": None,
            "currency": None,
            "conversion_rate": None,
        },
    }