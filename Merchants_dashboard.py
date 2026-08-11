import os
import logging
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import RedirectResponse
from typing import List, Optional
from pathlib import Path
import pandas as pd
import hmac

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 1. Initialize the FastAPI app instance
app = FastAPI(title="Shopify Merchants Intelligence API", version="1.0")

# Authorized tenant API keys mapping for secure multi-tenant isolation
VALID_TENANTS = {
    "merchant_001": "key_transparent_labs_secret_999",
    "merchant_002": "key_kaged_secret_888",
    "merchant_003": "key_ghost_secret_777",
    "merchant_004": "key_cellucor_secret_666",
    "merchant_005": "key_gorilla_secret_555",
    "merchant_006": "key_pescience_secret_444"
}

# --- Helper Classes & Functions ---

class ParquetStoreReader:
    @staticmethod
    def read_product_data(dataset_name: str, merchant_id: str) -> List[dict]:
        """Reads Gold layer Parquet datasets for a specific merchant using a deterministic path contract."""
        try:
            root_dir = Path(__file__).resolve().parent.parent
            
            # Deterministic Gold lake contract path mapping
            parquet_path = (
                root_dir
                / "Gold_Lake"
                / "Pricing_Intelligence"
                / "Shopify_Merchants"
                / merchant_id
                / dataset_name
                / "data.parquet"
            )

            logger.info(f"Reading Gold dataset: {parquet_path}")

            if not parquet_path.exists():
                logger.warning(
                    f"GOLD_NOT_FOUND | merchant={merchant_id} "
                    f"dataset={dataset_name} "
                    f"path={parquet_path}"
                )
                return []

            df = pd.read_parquet(parquet_path)

            # Validate internal tenant isolation integrity if column exists
            if "merchant_id" in df.columns:
                invalid = df[df["merchant_id"] != merchant_id]
                if not invalid.empty:
                    logger.error(f"Tenant isolation breach detected for merchant {merchant_id}")
                    raise HTTPException(
                        status_code=500,
                        detail="Gold tenant isolation validation failed."
                    )

            logger.info(
                f"GOLD_READ_SUCCESS | merchant={merchant_id} "
                f"dataset={dataset_name} "
                f"records={len(df)}"
            )

            return df.to_dict(orient="records")
            
        except HTTPException as he:
            raise he
        except Exception as e:
            logger.error(f"Error reading parquet for {dataset_name}: {e}", exc_info=True)
            return []

def verify_tenant_access(merchant_id: str, x_api_key: str) -> dict:
    """Verifies tenant authorization token securely using constant-time comparison."""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing API Key header.")
    
    expected_key = VALID_TENANTS.get(merchant_id)
    if not expected_key or not hmac.compare_digest(x_api_key, expected_key):
        raise HTTPException(status_code=403, detail="Invalid API Key or unauthorized tenant access.")
    
    return {
        "merchant_id": merchant_id,
        "store_url": f"https://merchant-{merchant_id}.myshopify.com"
    }

# --- API Routes ---

@app.get("/")
def root_landing():
    """Redirects the base URL straight to the interactive Swagger documentation."""
    return RedirectResponse(url="/docs")


@app.get("/api/v1/merchants/{merchant_id}/pricing-opportunities")
def get_pricing_opportunities(
    merchant_id: str,
    x_api_key: str = Header(..., alias="x-api-key")
):
    try:
        tenant = verify_tenant_access(merchant_id, x_api_key)
        
        # Use canonical dataset names matching the structured Gold contract
        records = ParquetStoreReader.read_product_data("product_pricing_opportunities", merchant_id)
        if not records:
            records = ParquetStoreReader.read_product_data("pricing_opportunities", merchant_id)
        
        return {
            "merchant_id": merchant_id,
            "store_url": tenant.get("store_url", ""),
            "record_count": len(records),
            "data": records
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error in pricing-opportunities: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/merchants/{merchant_id}/inventory-risks")
def get_inventory_risks(
    merchant_id: str,
    x_api_key: str = Header(..., alias="x-api-key")
):
    try:
        tenant = verify_tenant_access(merchant_id, x_api_key)

        records = ParquetStoreReader.read_product_data("inventory_risk", merchant_id)
        if not records:
            records = ParquetStoreReader.read_product_data("inventory_risks", merchant_id)

        return {
            "merchant_id": merchant_id,
            "store_url": tenant.get("store_url", ""),
            "record_count": len(records),
            "data": records
        }

    except HTTPException as he:
        raise he

    except Exception as e:
        logger.error(f"Error in inventory-risks: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("Merchants_serving:app", host="127.0.0.1", port=8000, reload=False)