"""Shopify intelligence pipeline package."""

from .analytics import get_market_insights
from .config import HEADERS as DEFAULT_HEADERS, MAX_CONCURRENCY, REQUEST_TIMEOUT, TARGET_STORES as TARGET_SEEDS
from .db_manager import init_db, save_to_db
from .engine import AsyncHttpWorker
from .graphql_client import fetch_storefront_graphql
from .normalizer import normalize_metrics, normalize_product_data
from .pipeline import run_pipeline

__all__ = [
    "AsyncHttpWorker",
    "DEFAULT_HEADERS",
    "MAX_CONCURRENCY",
    "REQUEST_TIMEOUT",
    "TARGET_SEEDS",
    "fetch_storefront_graphql",
    "get_market_insights",
    "init_db",
    "normalize_metrics",
    "normalize_product_data",
    "run_pipeline",
    "save_to_db",
]
