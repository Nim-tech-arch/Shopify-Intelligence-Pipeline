import os
import re
import logging
import hmac
import hashlib
from enum import Enum
from functools import lru_cache
from typing import List, Optional, Dict, Any
from pathlib import Path
from fastapi import FastAPI, Header, HTTPException, Depends, status, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")
logger = logging.getLogger("SIP_Serving_API")

# 1. Initialize FastAPI Application
app = FastAPI(
    title="Shopify Supplement Intelligence Pipeline API",
    description="Unified commercial intelligence layer delivering real-time pricing opportunities, inventory health, and cross-merchant competitive signals across 56 leading supplement brands.",
    version="2.5.0"
)

# Hard limit for public demo queries
MAX_DEMO_RECORD_LIMIT = 20

# 2. Top 10 Monitored Demo Merchant Enum for Swagger Drop-Down Selection
class DemoMerchantID(str, Enum):
    kaged = "kaged"
    transparentlabs = "transparentlabs"
    cellucor = "cellucor"
    nutricost = "nutricost"
    naturemade = "naturemade"
    appliednutrition_uk = "appliednutrition.uk"
    olly = "olly"
    nakednutrition = "nakednutrition"
    beekeepersnaturals = "beekeepersnaturals"
    codeage = "codeage"

# Store URL mapping helper
MERCHANT_STORE_URLS: Dict[str, str] = {
    "kaged": "https://www.kaged.com",
    "transparentlabs": "https://www.transparentlabs.com",
    "cellucor": "https://cellucor.com",
    "nutricost": "https://nutricost.com",
    "naturemade": "https://www.naturemade.com",
    "appliednutrition.uk": "https://appliednutrition.uk",
    "olly": "https://www.olly.com",
    "nakednutrition": "https://nakednutrition.com",
    "beekeepersnaturals": "https://beekeepersnaturals.com",
    "codeage": "https://www.codeage.com",
}

# --- PYDANTIC SCHEMAS ---

class ProductIntelligenceRecord(BaseModel):
    product_id: Optional[str] = None
    variant_id: Optional[str] = "N/A"
    product_title: Optional[str] = "Untitled Product"
    vendor: Optional[str] = "Unknown Vendor"
    price_usd: Optional[float] = 0.0
    market_median_price_usd: Optional[float] = 0.0
    price_variance_vs_market_pct: Optional[float] = 0.0
    review_count: Optional[int] = 0
    average_rating: Optional[float] = 0.0
    sentiment_score_positive: Optional[float] = 0.0
    has_active_ads: Optional[bool] = False
    active_creative_count: Optional[int] = 0
    brand_country_of_origin: Optional[str] = "UNKNOWN"

class StandardAPIResponse(BaseModel):
    merchant_id: str
    store_url: str
    record_count: int
    data: List[Dict[str, Any]]

# --- PUBLIC TENANT RESOLVER (NO PASSWORD / NO KEY REQUIRED) ---

def resolve_public_tenant(merchant_id: DemoMerchantID) -> Dict[str, str]:
    """Resolves merchant ID slug and canonical store URL without requiring authentication keys."""
    slug = merchant_id.value
    store_url = MERCHANT_STORE_URLS.get(slug, f"https://{slug}.com")
    return {
        "merchant_id": slug,
        "environment": "demo",
        "store_url": store_url
    }

# --- DATA LAKE READER SERVICE ---

class GoldLakeStoreReader:
    @staticmethod
    def resolve_workspace_root() -> Path:
        """Resolves workspace root from Serving_Shopify_Merchants directory flexibly."""
        script_dir = Path(__file__).resolve().parent
        return script_dir.parent if script_dir.name.lower() == "serving_shopify_merchants" else script_dir

    @classmethod
    @lru_cache(maxsize=8)
    def load_master_gold_dataset(cls, file_path_str: str) -> pd.DataFrame:
        """Cached in-memory reader for master Gold Lake JSON to eliminate repeated disk I/O."""
        path = Path(file_path_str)
        if not path.exists():
            return pd.DataFrame()
        logger.info(f"LOADING_MASTER_GOLD_LAKE_CACHE | path={path}")
        df = pd.read_json(path)
        return df.fillna(0).replace([float('inf'), float('-inf')], 0)

    @classmethod
    def read_enriched_products(cls, merchant_id: str, dataset_type: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Reads Gold Lake records, dynamically filters for requested merchant out of 56 stores, and caps results."""
        root_dir = cls.resolve_workspace_root()
        
        # Candidate Path 1: Domain-specific artifact JSON
        artifact_json = root_dir / "Shopify_supplements_enrichment" / "external_enrichment" / f"{dataset_type}.json"

        # Candidate Path 2: Merchant Partitioned Parquet Lake
        parquet_path = root_dir / "Gold_Lake" / "Pricing_Intelligence" / "Shopify_Merchants" / merchant_id / dataset_type / "data.parquet"
        
        # Candidate Path 3: Master External Enriched Gold JSON (Contains 20,078 records)
        master_gold_json = root_dir / "Gold_Lake" / "shopify_supplements_gold_external_enriched.json"

        try:
            if artifact_json.exists():
                df = cls.load_master_gold_dataset(str(artifact_json))
            elif parquet_path.exists():
                df = pd.read_parquet(parquet_path)
                df = df.fillna(0).replace([float('inf'), float('-inf')], 0)
            elif master_gold_json.exists():
                df = cls.load_master_gold_dataset(str(master_gold_json))
            else:
                logger.warning(f"GOLD_DATASET_NOT_FOUND | merchant={merchant_id} dataset={dataset_type}")
                return []

            if df.empty:
                return []

            # Dynamic Store Slug Matching across all 56 Stores
            clean_merchant = re.sub(r'[^a-zA-Z0-9]', '', merchant_id.lower())
            
            if any(col in df.columns for col in ["store_id", "vendor", "store_url"]):
                store_id_series = df.get("store_id", pd.Series()).astype(str).str.lower().str.replace(r'[^a-zA-Z0-9]', '', regex=True)
                vendor_series = df.get("vendor", pd.Series()).astype(str).str.lower().str.replace(r'[^a-zA-Z0-9]', '', regex=True)
                store_url_series = df.get("store_url", pd.Series()).astype(str).str.lower().str.replace(r'[^a-zA-Z0-9]', '', regex=True)

                mask = (
                    (store_id_series == clean_merchant) |
                    (vendor_series == clean_merchant) |
                    store_url_series.str.contains(clean_merchant, na=False)
                )
                
                filtered_df = df[mask]
                if not filtered_df.empty:
                    logger.info(f"DYNAMIC_STORE_FILTER_SUCCESS | merchant={merchant_id} dataset={dataset_type} records={len(filtered_df)}")
                    records = filtered_df.to_dict(orient="records")
                    return records[:min(limit, MAX_DEMO_RECORD_LIMIT)]

            records = df.to_dict(orient="records")
            return records[:min(limit, MAX_DEMO_RECORD_LIMIT)]

        except Exception as e:
            logger.error(f"Error reading dataset '{dataset_type}' for {merchant_id}: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to load Gold dataset '{dataset_type}'."
            )

# --- ROUTES ---

@app.get("/", include_in_schema=False)
def root_landing():
    """Redirects root URL directly to Swagger documentation."""
    return RedirectResponse(url="/docs")

# --- 1. PRICING & UNIT ECONOMICS ---

@app.get(
    "/api/v1/merchants/{merchant_id}/pricing-opportunities",
    response_model=StandardAPIResponse,
    tags=["1. Pricing & Unit Economics"]
)
def get_pricing_opportunities(
    merchant_id: DemoMerchantID,
    limit: int = Query(default=20, ge=1, le=20, description="Maximum records to return (capped at 20)")
):
    """Exposes competitive pricing variance, market median prices, and unit economic benchmarking."""
    tenant = resolve_public_tenant(merchant_id)
    records = GoldLakeStoreReader.read_enriched_products(merchant_id.value, "pricing_opportunities", limit=limit)
    
    return StandardAPIResponse(
        merchant_id=merchant_id.value,
        store_url=tenant["store_url"],
        record_count=len(records),
        data=records
    )

# --- 2. INVENTORY & STOCK ANALYTICS ---

@app.get(
    "/api/v1/merchants/{merchant_id}/inventory-risks",
    response_model=StandardAPIResponse,
    tags=["2. Inventory & Stock Analytics"]
)
def get_inventory_risks(
    merchant_id: DemoMerchantID,
    limit: int = Query(default=20, ge=1, le=20, description="Maximum records to return (capped at 20)")
):
    """Exposes stockout velocity metrics, historical availability rates, and inventory risk levels."""
    tenant = resolve_public_tenant(merchant_id)
    records = GoldLakeStoreReader.read_enriched_products(merchant_id.value, "inventory_risks", limit=limit)

    return StandardAPIResponse(
        merchant_id=merchant_id.value,
        store_url=tenant["store_url"],
        record_count=len(records),
        data=records
    )

# --- 3. CUSTOMER REVIEW SENTIMENT ---

@app.get(
    "/api/v1/merchants/{merchant_id}/reviews-sentiment",
    response_model=StandardAPIResponse,
    tags=["3. Customer Review Sentiment"]
)
def get_review_sentiment(
    merchant_id: DemoMerchantID,
    limit: int = Query(default=20, ge=1, le=20, description="Maximum records to return (capped at 20)")
):
    """Exposes review counts, average star ratings, positive/negative sentiment ratios, and widget providers."""
    tenant = resolve_public_tenant(merchant_id)
    records = GoldLakeStoreReader.read_enriched_products(merchant_id.value, "review_sentiment_metrics", limit=limit)

    return StandardAPIResponse(
        merchant_id=merchant_id.value,
        store_url=tenant["store_url"],
        record_count=len(records),
        data=records
    )

# --- 4. SEO & ORGANIC VISIBILITY ---

@app.get(
    "/api/v1/merchants/{merchant_id}/seo-visibility",
    response_model=StandardAPIResponse,
    tags=["4. SEO & Organic Visibility"]
)
def get_seo_visibility(
    merchant_id: DemoMerchantID,
    limit: int = Query(default=20, ge=1, le=20, description="Maximum records to return (capped at 20)")
):
    """Exposes target keywords, monthly search volume, organic search rankings, and search intent flags."""
    tenant = resolve_public_tenant(merchant_id)
    records = GoldLakeStoreReader.read_enriched_products(merchant_id.value, "seo_visibility_metrics", limit=limit)

    return StandardAPIResponse(
        merchant_id=merchant_id.value,
        store_url=tenant["store_url"],
        record_count=len(records),
        data=records
    )

# --- 5. PAID ADVERTISING INTELLIGENCE ---

@app.get(
    "/api/v1/merchants/{merchant_id}/ad-intelligence",
    response_model=StandardAPIResponse,
    tags=["5. Paid Ad Intelligence"]
)
def get_ad_intelligence(
    merchant_id: DemoMerchantID,
    limit: int = Query(default=20, ge=1, le=20, description="Maximum records to return (capped at 20)")
):
    """Exposes active creative counts across Meta and TikTok, ad platforms, and campaign durations."""
    tenant = resolve_public_tenant(merchant_id)
    records = GoldLakeStoreReader.read_enriched_products(merchant_id.value, "ad_intelligence_metrics", limit=limit)

    return StandardAPIResponse(
        merchant_id=merchant_id.value,
        store_url=tenant["store_url"],
        record_count=len(records),
        data=records
    )

# --- 6. CORPORATE BRAND & GEO INTELLIGENCE ---

@app.get(
    "/api/v1/merchants/{merchant_id}/brand-intelligence",
    response_model=StandardAPIResponse,
    tags=["6. Corporate Brand Intelligence"]
)
def get_brand_intelligence(
    merchant_id: DemoMerchantID,
    limit: int = Query(default=20, ge=1, le=20, description="Maximum records to return (capped at 20)")
):
    """Exposes HQ country of origin, estimated web session traffic, market positioning, and social reach."""
    tenant = resolve_public_tenant(merchant_id)
    records = GoldLakeStoreReader.read_enriched_products(merchant_id.value, "brand_geo_intelligence", limit=limit)

    return StandardAPIResponse(
        merchant_id=merchant_id.value,
        store_url=tenant["store_url"],
        record_count=len(records),
        data=records
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("Merchants_serving:app", host="127.0.0.1", port=8000, reload=True)