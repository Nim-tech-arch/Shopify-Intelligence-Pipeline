"""Utilities to clean, flatten, and extract monetization metrics."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _extract_graphql_products(raw_products: Any) -> list[dict[str, Any]]:
    """Convert Shopify Storefront GraphQL payloads into the product structure expected by the normalizer."""
    if not isinstance(raw_products, dict):
        return []

    data = raw_products.get("data")
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
                            "inventory_quantity": variant_node.get("quantityAvailable"),
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


def _parse_float(value: Any, default: float = 0.0) -> float:
    if value in (None, "", []):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _parse_int(value: Any, default: int = 0) -> int:
    if value in (None, "", []):
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _extract_products(raw_products: Any) -> list[dict[str, Any]]:
    graphql_products = _extract_graphql_products(raw_products)
    if graphql_products:
        return graphql_products

    if isinstance(raw_products, dict):
        if isinstance(raw_products.get("products"), list):
            return [item for item in raw_products.get("products", []) if isinstance(item, dict)]
        if isinstance(raw_products.get("product"), dict):
            return [raw_products["product"]]
        return []

    if isinstance(raw_products, list):
        return [item for item in raw_products if isinstance(item, dict)]

    return []


def normalize_product_data(store_url: str, raw_products: list[dict[str, Any]] | dict[str, Any] | None) -> list[dict[str, Any]]:
    """Flatten product and variant data into a record per variant for BI analysis."""
    flat_records: list[dict[str, Any]] = []
    crawl_timestamp = datetime.now(timezone.utc).isoformat()

    for product in _extract_products(raw_products):
        product_id = product.get("id")
        title = product.get("title")
        handle = product.get("handle")
        vendor = product.get("vendor")
        product_type = product.get("product_type")

        variants = product.get("variants") if isinstance(product.get("variants"), list) else []
        if not variants:
            continue

        for variant in variants:
            if not isinstance(variant, dict):
                continue

            variant_id = variant.get("id")
            variant_title = variant.get("title")
            sku = variant.get("sku")

            price = _parse_float(variant.get("price"), 0.0)
            compare_price_float = _parse_float(variant.get("compare_at_price"), price)
            discount_spread = round(max(0.0, compare_price_float - price), 2)
            available_value = variant.get("availableForSale", variant.get("available", False))
            if isinstance(available_value, str):
                available = available_value.strip().lower() in {"1", "true", "yes", "y", "on"}
            elif available_value is None:
                available = False
            else:
                available = bool(available_value)
            inventory_qty = _parse_int(variant.get("quantityAvailable", variant.get("inventory_quantity", 0)), 0)

            flat_records.append(
                {
                    "store_url": store_url,
                    "crawl_timestamp": crawl_timestamp,
                    "product_id": product_id,
                    "product_title": title,
                    "product_handle": handle,
                    "vendor": vendor,
                    "product_type": product_type,
                    "variant_id": variant_id,
                    "variant_title": variant_title,
                    "sku": sku,
                    "price": price,
                    "compare_at_price": compare_price_float,
                    "discount_spread": discount_spread,
                    "available": available,
                    "inventory_quantity": inventory_qty,
                }
            )

    return flat_records


def normalize_metrics(payload: dict[str, Any]) -> dict[str, Any]:
    """Normalize a raw payload into a simple, flat structure."""
    flattened = {
        "url": payload.get("url"),
        "status_code": payload.get("status_code"),
        "content_length": len(payload.get("text", "")),
    }

    monetization = {
        "revenue": None,
        "currency": None,
        "conversion_rate": None,
    }

    return {"metrics": flattened, "monetization": monetization}
