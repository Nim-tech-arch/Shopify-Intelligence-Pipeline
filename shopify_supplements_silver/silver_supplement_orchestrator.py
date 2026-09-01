"""Silver Layer Orchestrator for the Shopify Supplement Intelligence Pipeline."""

import json
import logging
import re
import sqlite3
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Path Resolutions
# ---------------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent

BRONZE_JSON = ROOT_DIR / "shopify_supplement_intelligence.json"
BRONZE_DB = ROOT_DIR / "shopify_intelligence.db"  # Fixed typo: added .db extension
SILVER_DB = ROOT_DIR / "shopify_silver_intelligence.db"
SILVER_JSON = ROOT_DIR / "shopify_supplements_silver.json"

# ---------------------------------------------------------------------------
# Configuration & Lookups
# ---------------------------------------------------------------------------
_GID_PATTERN = re.compile(r"gid://shopify/\w+/(\d+)")

FX_TO_USD: Dict[str, float] = {
    "USD": 1.0,
    "AUD": 0.65,
    "GBP": 1.27,
    "EUR": 1.08,
    "CAD": 0.73,
    "NZD": 0.59,
    "KES": 0.0078,
    "NGN": 0.00062,
    "PKR": 0.0036,
    "ZAR": 0.055,
    "INR": 0.012,
    "AED": 0.27,
}

STORE_CURRENCY_OVERRIDES: Dict[str, str] = {
    "starsamnaturals.com": "KES",
    "wassen.com": "GBP",
}

TLD_CURRENCY_MAP: Dict[str, str] = {
    ".com.au": "AUD",
    ".co.uk": "GBP",
    ".org.uk": "GBP",
    ".au": "AUD",
    ".uk": "GBP",
    ".ca": "CAD",
    ".nz": "NZD",
    ".de": "EUR",
    ".fr": "EUR",
    ".ie": "EUR",
    ".co.ke": "KES",
    ".ng": "NGN",
    ".pk": "PKR",
    ".co.za": "ZAR",
    ".in": "INR",
    ".ae": "AED",
}

CATEGORY_TAXONOMY = [
    ("PROTEIN", ["protein", "whey", "casein", "coreseries", "proteinseries"]),
    ("AMINO_ACIDS", ["amino", "bcaa", "eaa", "glutamine", "5-htp", "5htp"]),
    ("COLLAGEN", ["collagen"]),
    ("MINERALS", ["mineral", "magnesium", "calcium", "zinc", "iron", "electrolyte"]),
    ("VITAMINS", ["vitamin", "multivitamin"]),
    ("PRE_WORKOUT", ["pre-workout", "pre workout", "preworkout", "preseries"]),
    ("CREATINE", ["creatine"]),
    ("PROBIOTICS", ["probiotic", "digestive", "gut"]),
    ("HERBAL", ["herbal", "herb"]),
    ("ENERGY", ["energy drink", "energy", "caffeine"]),
    ("GUMMIES", ["gummy", "gummies"]),
    ("SUPERFOOD", ["superfood", "greens", "broth"]),
    ("BUNDLE", ["bundle", "stack", "kit", "sample"]),
    ("APPAREL", ["apparel", "accessories", "accessory"]),
    ("SUPPLEMENT_GENERAL", ["supplement"]),
]

# ---------------------------------------------------------------------------
# Vectorized Helpers
# ---------------------------------------------------------------------------
def normalize_id_series(series: pd.Series) -> pd.Series:
    """Vectorized normalization of product/variant IDs."""
    str_series = series.fillna("").astype(str).str.strip()
    extracted = str_series.str.extract(_GID_PATTERN, expand=False)
    return extracted.fillna(str_series)


def derive_currency_series(store_urls: pd.Series) -> pd.Series:
    """Vectorized extraction of native currency based on domain overrides & TLDs."""
    domains = (
        store_urls.fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"^https?://", "", regex=True)
        .str.rstrip("/")
        .str.split("/")
        .str[0]
        .str.replace(r"^www\.", "", regex=True)
    )

    currencies = pd.Series("USD", index=domains.index)

    # 1. Apply TLD matches (shortest to longest suffix)
    for suffix, curr in sorted(TLD_CURRENCY_MAP.items(), key=lambda x: len(x[0])):
        mask = domains.str.endswith(suffix)
        currencies[mask] = curr

    # 2. Apply explicit store overrides
    for store_domain, curr in STORE_CURRENCY_OVERRIDES.items():
        mask = domains == store_domain
        currencies[mask] = curr

    return currencies


def load_bronze_dataframe() -> pd.DataFrame:
    """Loads Bronze dataset from JSON or SQLite fallback."""
    if BRONZE_JSON.exists():
        try:
            with open(BRONZE_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)
            df = pd.DataFrame(data)
            logger.info("Loaded %d records from Bronze JSON: %s", len(df), BRONZE_JSON)
            return df
        except Exception as exc:
            logger.error("Failed to read Bronze JSON: %s", exc)

    if BRONZE_DB.exists():
        try:
            with sqlite3.connect(BRONZE_DB) as conn:
                df = pd.read_sql("SELECT * FROM product_snapshots", conn)
            logger.info("Loaded %d records from Bronze SQLite DB: %s", len(df), BRONZE_DB)
            return df
        except Exception as exc:
            logger.error("Failed to read Bronze SQLite DB: %s", exc)

    logger.error("No valid Bronze dataset found.")
    return pd.DataFrame()


def run_silver_orchestrator() -> None:
    logger.info("Initializing Silver Layer Orchestration...")
    df = load_bronze_dataframe()

    if df.empty:
        logger.warning("No records found in Bronze layer. Exiting pipeline.")
        return

    expected_cols = [
        "store_url", "crawl_timestamp", "product_id", "product_title",
        "product_handle", "vendor", "product_type", "variant_id",
        "variant_title", "sku", "currency", "price", "compare_at_price",
        "discount_spread", "available", "inventory_quantity",
    ]
    for col in expected_cols:
        if col not in df.columns:
            df[col] = None

    # 1. Schema Standardization & Type Coercion
    logger.info("Applying schema standardization & type coercion...")
    df["store_url"] = df["store_url"].astype(str).str.strip().str.lower()
    df["product_title"] = df["product_title"].astype(str).str.strip()
    df["variant_title"] = df["variant_title"].astype(str).str.strip()
    df["vendor"] = df["vendor"].fillna("Unknown Vendor").astype(str).str.strip()
    
    df["product_id"] = normalize_id_series(df["product_id"])
    df["variant_id"] = normalize_id_series(df["variant_id"])

    # Timestamps
    df["crawl_timestamp"] = pd.to_datetime(df["crawl_timestamp"], errors="coerce", utc=True)
    df["crawl_timestamp"] = df["crawl_timestamp"].fillna(pd.Timestamp.now(tz="UTC"))
    df["crawl_timestamp"] = df["crawl_timestamp"].dt.floor("s").dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    # Numeric Coercion
    df["price_native"] = pd.to_numeric(df["price"], errors="coerce").fillna(0.0).round(2)
    df["compare_at_price_native"] = pd.to_numeric(df["compare_at_price"], errors="coerce").fillna(df["price_native"]).round(2)
    df["inventory_quantity"] = pd.to_numeric(df["inventory_quantity"], errors="coerce").fillna(0).astype("int64")
    df["available"] = df["available"].fillna(False).astype(bool)

    # 2. Currency Normalization & FX Conversion
    logger.info("Correcting currency mislabeling and converting to USD...")
    df["currency_raw"] = derive_currency_series(df["store_url"])
    fx_rates = df["currency_raw"].map(FX_TO_USD).fillna(1.0)
    
    # 3. Discount Sanity Checks & USD Calculations
    logger.info("Applying discount sanity checks and computing USD metrics...")
    invalid_discount = df["price_native"] > df["compare_at_price_native"]
    df.loc[invalid_discount, "compare_at_price_native"] = df.loc[invalid_discount, "price_native"]

    df["discount_spread"] = (df["compare_at_price_native"] - df["price_native"]).clip(lower=0.0).round(2)
    df["price_usd"] = (df["price_native"] * fx_rates).round(2)
    df["compare_at_price_usd"] = (df["compare_at_price_native"] * fx_rates).round(2)

    df["discount_pct"] = np.where(
        (df["compare_at_price_usd"] > df["price_usd"]) & (df["price_usd"] > 0),
        ((df["compare_at_price_usd"] - df["price_usd"]) / df["compare_at_price_usd"] * 100).round(2),
        0.0,
    )
    df["is_promotional_gift"] = df["price_usd"] == 0.0

    # 4. Inventory Metrics
    logger.info("Computing stock availability metrics...")
    df["is_in_stock"] = df["available"] & (df["inventory_quantity"] >= 0)
    
    stores_with_tracking = set(df.loc[df["inventory_quantity"] != 0, "store_url"].unique())
    df["quantity_tracked"] = df["store_url"].isin(stores_with_tracking)

    df["stock_status"] = np.select(
        [
            ~df["is_in_stock"],
            df["quantity_tracked"] & (df["inventory_quantity"] > 0) & (df["inventory_quantity"] <= 5),
        ],
        ["OUT_OF_STOCK", "LOW_STOCK_WARNING"],
        default="IN_STOCK",
    )

    # 5. Data Quality Scoring (Vectorized)
    logger.info("Computing Data Quality Scores...")
    dqs = pd.Series(100, index=df.index)
    
    # Deduct 20 if SKU is missing
    sku_invalid = df["sku"].isna() | df["sku"].astype(str).str.strip().str.lower().isin(["", "none", "nan"])
    dqs -= np.where(sku_invalid, 20, 0)

    # Deduct 30 if Generic Title
    generic_titles = {"default title", "default variant", ""}
    product_title_gen = df["product_title"].str.lower().isin(generic_titles)
    variant_title_gen = df["variant_title"].str.lower().isin(generic_titles)
    dqs -= np.where(product_title_gen | variant_title_gen, 30, 0)

    # Deduct 50 if Price <= 0
    dqs -= np.where(df["price_native"] <= 0, 50, 0)

    df["data_quality_score"] = dqs.clip(lower=0, upper=100).astype("int64")

    # 6. Deduplication
    logger.info("Performing primary-key deduplication...")
    before_count = len(df)
    df = df.sort_values("data_quality_score", ascending=False).drop_duplicates(
        subset=["store_url", "product_id", "variant_id", "crawl_timestamp"], keep="first"
    )
    logger.info("Removed %d duplicate record(s).", before_count - len(df))

    # 7. Final Schema Projection & Persistence
    df["store_id"] = df["store_url"]

    # Provide defaults for non-vectorized category/size columns if needed
    df["category"] = "SUPPLEMENT_GENERAL"
    df["serving_count"] = 0
    df["package_size_g"] = 0.0
    df["package_unit"] = ""
    df["price_per_unit_usd"] = 0.0

    silver_schema_columns = [
        "store_id", "store_url", "crawl_timestamp", "product_id", "variant_id",
        "product_title", "variant_title", "sku", "vendor", "category",
        "currency_raw", "price_native", "price_usd", "compare_at_price_usd",
        "discount_pct", "discount_spread", "is_promotional_gift", "serving_count",
        "package_size_g", "package_unit", "price_per_unit_usd", "is_in_stock",
        "stock_status", "inventory_quantity", "data_quality_score",
    ]

    silver_df = df[silver_schema_columns].sort_values(["store_id", "product_id", "variant_id"]).reset_index(drop=True)

    # Save to SQLite & JSON
    with sqlite3.connect(SILVER_DB) as conn:
        silver_df.to_sql("silver_products", conn, if_exists="replace", index=False)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_silver_identity ON silver_products(store_id, product_id, variant_id);")

    silver_df.to_json(SILVER_JSON, orient="records", indent=4)
    logger.info("Silver Layer Orchestration Complete. Saved %d records to %s & %s", len(silver_df), SILVER_DB, SILVER_JSON)


if __name__ == "__main__":
    run_silver_orchestrator()