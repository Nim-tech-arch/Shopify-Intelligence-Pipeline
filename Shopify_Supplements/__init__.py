"""Shopify Supplements Ingestion Package."""

from .analytics import fetch_latest_market_insights, print_market_insights_dashboard
from .config import DEFAULT_HEADERS, HEADERS, TARGET_STORES
from .db_manager import save_to_db
from .engine import AsyncHttpWorker, fetch_catalog
from .normalizer import normalize_product_data

__all__ = [
    "fetch_latest_market_insights",
    "print_market_insights_dashboard",
    "save_to_db",
    "AsyncHttpWorker",
    "fetch_catalog",
    "normalize_product_data",
    "TARGET_STORES",
    "HEADERS",
    "DEFAULT_HEADERS",
]