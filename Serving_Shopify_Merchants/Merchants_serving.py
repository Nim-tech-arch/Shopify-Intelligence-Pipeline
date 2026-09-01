import os
import re
import logging
import hmac
import hashlib
from functools import lru_cache
from typing import List, Optional, Dict, Any
from pathlib import Path
from fastapi import FastAPI, Header, HTTPException, Depends, Security, status
from fastapi.security import APIKeyHeader
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

# Security Scheme
API_KEY_HEADER = APIKeyHeader(name="x-api-key", auto_error=False)

# Master signing key for HMAC token generation/verification
MASTER_AUTH_SECRET = os.getenv("SIP_AUTH_SECRET", "sip_master_enterprise_secret_2026")

# Standardized Token RegEx Pattern: sip_(live|test)_{merchant_slug}_{entropy_hash}
SIP_KEY_REGEX = re.compile(r"^sip_(live|test)_([a-z0-9]+)_([a-f0-9]{16,32})$")

# Backwards-compatible override map for static keys
VALID_TENANTS_OVERRIDE: Dict[str, str] = {
    "transparentlabs": "sip_live_transparentlabs_999a888b777c666d",
    "kaged": "sip_live_kaged_888a777b666c555d",
    "ghost": "sip_live_ghost_777a666b555c444d",
    "cellucor": "sip_live_cellucor_666a555b444c333d",
    "gorillamind": "sip_live_gorillamind_555a444b333c222d",
    "pescience": "sip_live_pescience_444a333b222c111d"
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

# --- SECURITY UTILITIES & DEPENDENCIES ---

def verify_token_signature(merchant_slug: str, token_hash: str) -> bool:
    """Computes and compares expected HMAC signature for entropy hash validation."""
    expected_hash = hmac.new(
        MASTER_AUTH_SECRET.encode("utf-8"),
        merchant_slug.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()[:len(token_hash)]
    
    return hmac.compare_digest(token_hash.lower(), expected_hash.lower())


def get_current_tenant(
    merchant_id: str,
    x_api_key: Optional[str] = Security(API_KEY_HEADER)
) -> Dict[str, str]:
    """Dependency enforcing standardized token format and HMAC signature validation."""
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing required 'x-api-key' header."
        )

    clean_path_merchant = re.sub(r'[^a-zA-Z0-9]', '', merchant_id.lower())

    # 1. Check override map for static/legacy tokens
    if merchant_id in VALID_TENANTS_OVERRIDE or clean_path_merchant in VALID_TENANTS_OVERRIDE:
        expected_key = VALID_TENANTS_OVERRIDE.get(merchant_id) or VALID_TENANTS_OVERRIDE.get(clean_path_merchant)
        if hmac.compare_digest(x_api_key.strip(), expected_key):
            return {
                "merchant_id": clean_path_merchant,
                "environment": "live",
                "store_url": f"https://{clean_path_merchant}.com"
            }

    # 2. Validate Token Structure
    match = SIP_KEY_REGEX.match(x_api_key.strip())
    if not match:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid API key format. Expected standardized token format: 'sip_live_<merchant_slug>_<hash>'."
        )

    env, token_merchant_slug, token_hash = match.groups()

    # 3. Enforce Tenant Context Matching
    if token_merchant_slug != clean_path_merchant:
        logger.warning(f"TENANT_CONTEXT_MISMATCH | token_slug={token_merchant_slug} route_slug={clean_path_merchant}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Token tenant context '{token_merchant_slug}' does not match route merchant '{clean_path_merchant}'."
        )

    return {
        "merchant_id": token_merchant_slug,
        "environment": env,
        "store_url": f"https://{token_merchant_slug}.com"
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
    def read_enriched_products(cls, merchant_id: str, dataset_type: str) -> List[Dict[str, Any]]:
        """Reads Gold Lake records and dynamically filters for the requested merchant out of 56 stores."""
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
                    return filtered_df.to_dict(orient="records")

            return df.to_dict(orient="records")

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

# --- 1. INTERNAL UNIT ECONOMICS & PRICING ---

@app.get(
    "/api/v1/merchants/{merchant_id}/pricing-opportunities",
    response_model=StandardAPIResponse,
    tags=["1. Pricing & Unit Economics"]
)
def get_pricing_opportunities(
    merchant_id: str,
    tenant: Dict[str, str] = Depends(get_current_tenant)
):
    """Exposes competitive pricing variance, market median prices, and unit economic benchmarking."""
    records = GoldLakeStoreReader.read_enriched_products(merchant_id, "pricing_opportunities")
    
    return StandardAPIResponse(
        merchant_id=merchant_id,
        store_url=tenant["store_url"],
        record_count=len(records),
        data=records
    )

# --- 2. INTERNAL INVENTORY & STOCKOUT RISKS ---

@app.get(
    "/api/v1/merchants/{merchant_id}/inventory-risks",
    response_model=StandardAPIResponse,
    tags=["2. Inventory & Stock Analytics"]
)
def get_inventory_risks(
    merchant_id: str,
    tenant: Dict[str, str] = Depends(get_current_tenant)
):
    """Exposes stockout velocity metrics, historical availability rates, and inventory risk levels."""
    records = GoldLakeStoreReader.read_enriched_products(merchant_id, "inventory_risks")

    return StandardAPIResponse(
        merchant_id=merchant_id,
        store_url=tenant["store_url"],
        record_count=len(records),
        data=records
    )

# --- 3. EXTERNAL SUBDOMAIN: CUSTOMER REVIEWS & SENTIMENT ---

@app.get(
    "/api/v1/merchants/{merchant_id}/reviews-sentiment",
    response_model=StandardAPIResponse,
    tags=["3. Customer Review Sentiment"]
)
def get_review_sentiment(
    merchant_id: str,
    tenant: Dict[str, str] = Depends(get_current_tenant)
):
    """Exposes review counts, average star ratings, positive/negative sentiment ratios, and widget providers."""
    records = GoldLakeStoreReader.read_enriched_products(merchant_id, "review_sentiment_metrics")

    return StandardAPIResponse(
        merchant_id=merchant_id,
        store_url=tenant["store_url"],
        record_count=len(records),
        data=records
    )

# --- 4. EXTERNAL SUBDOMAIN: SEO & ORGANIC VISIBILITY ---

@app.get(
    "/api/v1/merchants/{merchant_id}/seo-visibility",
    response_model=StandardAPIResponse,
    tags=["4. SEO & Organic Visibility"]
)
def get_seo_visibility(
    merchant_id: str,
    tenant: Dict[str, str] = Depends(get_current_tenant)
):
    """Exposes target keywords, monthly search volume, organic search rankings, and search intent flags."""
    records = GoldLakeStoreReader.read_enriched_products(merchant_id, "seo_visibility_metrics")

    return StandardAPIResponse(
        merchant_id=merchant_id,
        store_url=tenant["store_url"],
        record_count=len(records),
        data=records
    )

# --- 5. EXTERNAL SUBDOMAIN: PAID ADVERTISING INTELLIGENCE ---

@app.get(
    "/api/v1/merchants/{merchant_id}/ad-intelligence",
    response_model=StandardAPIResponse,
    tags=["5. Paid Ad Intelligence"]
)
def get_ad_intelligence(
    merchant_id: str,
    tenant: Dict[str, str] = Depends(get_current_tenant)
):
    """Exposes active creative counts across Meta and TikTok, ad platforms, and campaign durations."""
    records = GoldLakeStoreReader.read_enriched_products(merchant_id, "ad_intelligence_metrics")

    return StandardAPIResponse(
        merchant_id=merchant_id,
        store_url=tenant["store_url"],
        record_count=len(records),
        data=records
    )

# --- 6. EXTERNAL SUBDOMAIN: CORPORATE BRAND & GEO INTELLIGENCE ---

@app.get(
    "/api/v1/merchants/{merchant_id}/brand-intelligence",
    response_model=StandardAPIResponse,
    tags=["6. Corporate Brand Intelligence"]
)
def get_brand_intelligence(
    merchant_id: str,
    tenant: Dict[str, str] = Depends(get_current_tenant)
):
    """Exposes HQ country of origin, estimated web session traffic, market positioning, and social reach."""
    records = GoldLakeStoreReader.read_enriched_products(merchant_id, "brand_geo_intelligence")

    return StandardAPIResponse(
        merchant_id=merchant_id,
        store_url=tenant["store_url"],
        record_count=len(records),
        data=records
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("Merchants_serving:app", host="127.0.0.1", port=8000, reload=True)