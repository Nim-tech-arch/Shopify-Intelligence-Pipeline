import os
import time
import hmac
import hashlib
import uuid
import json
import asyncio
import logging
import random
import sqlite3
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pathlib import Path
from contextlib import asynccontextmanager

import pandas as pd
import httpx
from fastapi import FastAPI, HTTPException, Header, BackgroundTasks
from pydantic import BaseModel, Field

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MerchantServingLayer")

# Configuration Paths
GOLD_OUTPUT_DIR = Path(r"C:\Users\USER\OneDrive\Desktop\REPOS\GITrepos\Shopify-Intelligence-Pipeline\Gold_Lake\Pricing_Intelligence\Shopify_Merchants")
DB_PATH = Path("webhook_state.db")

# Authorized Tenants
VALID_TENANTS = {
    "merchant_001": {
        "name": "Transparent Labs",
        "store_url": "transparent-labs.myshopify.com",
        "webhook_endpoint": os.environ.get("TL_WEBHOOK_ENDPOINT", "https://transparent-labs.myshopify.com/webhook-receiver"),
        "api_key": os.environ.get("TL_API_KEY", "tl_test_key_123"),
        "webhook_secret": os.environ.get("TL_WEBHOOK_SECRET", "tl_secret_123")
    },
    "merchant_002": {
        "name": "Kaged",
        "store_url": "kaged.myshopify.com",
        "webhook_endpoint": os.environ.get("KAGED_WEBHOOK_ENDPOINT", "https://kaged.myshopify.com/webhook-receiver"),
        "api_key": os.environ.get("KAGED_API_KEY", "kaged_test_key_123"),
        "webhook_secret": os.environ.get("KAGED_SECRET", "kaged_secret_123")
    },
    "merchant_003": {
        "name": "Ghost Lifestyle",
        "store_url": "ghost-lifestyle.myshopify.com",
        "webhook_endpoint": os.environ.get("GHOST_WEBHOOK_ENDPOINT", "https://ghost-lifestyle.myshopify.com/webhook-receiver"),
        "api_key": os.environ.get("GHOST_API_KEY", "ghost_test_key_123"),
        "webhook_secret": os.environ.get("GHOST_SECRET", "ghost_secret_123")
    },
    "merchant_004": {
        "name": "Cellucor",
        "store_url": "cellucor.myshopify.com",
        "webhook_endpoint": os.environ.get("CELLUCOR_WEBHOOK_ENDPOINT", "https://cellucor.myshopify.com/webhook-receiver"),
        "api_key": os.environ.get("CELLUCOR_API_KEY", "cellucor_test_key_123"),
        "webhook_secret": os.environ.get("CELLUCOR_SECRET", "cellucor_secret_123")
    },
    "merchant_005": {
        "name": "Gorilla Mind",
        "store_url": "gorilla-mind.myshopify.com",
        "webhook_endpoint": os.environ.get("GORILLA_WEBHOOK_ENDPOINT", "https://gorilla-mind.myshopify.com/webhook-receiver"),
        "api_key": os.environ.get("GORILLA_API_KEY", "gorilla_test_key_123"),
        "webhook_secret": os.environ.get("GORILLA_SECRET", "gorilla_secret_123")
    },
    "merchant_006": {
        "name": "PE Science",
        "store_url": "pe-science.myshopify.com",
        "webhook_endpoint": os.environ.get("PES_WEBHOOK_ENDPOINT", "https://pe-science.myshopify.com/webhook-receiver"),
        "api_key": os.environ.get("PES_API_KEY", "pes_test_key_123"),
        "webhook_secret": os.environ.get("PES_SECRET", "pes_secret_123")
    }
}

# ==========================================
# 1. PERSISTENT STORAGE (SQLite DLQ & Logs)
# ==========================================
class PersistentWebhookStore:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS delivery_logs (
                    delivery_id TEXT PRIMARY KEY,
                    event_id TEXT,
                    merchant_id TEXT,
                    event_type TEXT,
                    status TEXT,
                    attempts INTEGER,
                    error TEXT,
                    timestamp TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS dead_letter_queue (
                    event_id TEXT PRIMARY KEY,
                    delivery_id TEXT,
                    merchant_id TEXT,
                    event_type TEXT,
                    payload TEXT,
                    error TEXT,
                    failed_at TEXT
                )
            """)
            conn.commit()

    def log_delivery(self, delivery_id: str, event_id: str, merchant_id: str, event_type: str, status: str, attempts: int, error: Optional[str] = None):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO delivery_logs (delivery_id, event_id, merchant_id, event_type, status, attempts, error, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (delivery_id, event_id, merchant_id, event_type, status, attempts, error, datetime.now(timezone.utc).isoformat()))
            conn.commit()

    def add_to_dlq(self, event_id: str, delivery_id: str, merchant_id: str, event_type: str, payload: dict, error: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO dead_letter_queue (event_id, delivery_id, merchant_id, event_type, payload, error, failed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (event_id, delivery_id, merchant_id, event_type, json.dumps(payload), error, datetime.now(timezone.utc).isoformat()))
            conn.commit()

    def get_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM delivery_logs ORDER BY timestamp DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def get_dlq(self) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM dead_letter_queue")
            return [dict(row) for row in cursor.fetchall()]

db_store = PersistentWebhookStore()

# ==========================================
# 2. LIFESPAN & APPLICATION SETUP
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Corrected lifespan: validates all configurations before yielding to start."""
    for m_id, info in VALID_TENANTS.items():
        if not info["api_key"] or not info["webhook_secret"]:
            logger.warning(f"Configuration warning: Missing secrets for {info['name']} ({m_id})")
        else:
            logger.info(f"Loaded tenant configuration successfully: {info['name']} ({m_id})")
    yield

app = FastAPI(
    title="Shopify Merchant Intelligence Serving API",
    version="2.4.4",
    description="Multi-tenant serving layer with SQLite persistence, anti-replay signatures, and correct lifespan scope.",
    lifespan=lifespan
)

# ==========================================
# 3. SECURITY & TENANT AUTHENTICATION
# ==========================================
def verify_tenant_access(merchant_id: str, x_api_key: str = Header(...)) -> Dict[str, str]:
    if merchant_id not in VALID_TENANTS:
        raise HTTPException(status_code=403, detail="Merchant identifier not recognized.")
    
    tenant_info = VALID_TENANTS[merchant_id]
    
    if not tenant_info["api_key"]:
        raise HTTPException(status_code=500, detail="Tenant API key not configured on server.")

    if not hmac.compare_digest(tenant_info["api_key"].encode('utf-8'), x_api_key.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid API key for this tenant.")
    
    return tenant_info

# ==========================================
# 4. DATA ACCESS LAYER (PARQUET READER)
# ==========================================
class ParquetStoreReader:
    @staticmethod
    def read_product_data(category: str, store_url: str) -> List[Dict[str, Any]]:
        parquet_path = GOLD_OUTPUT_DIR / category / "data.parquet"
        if not parquet_path.exists():
            return []
        df = pd.read_parquet(parquet_path)
        if "store_url" not in df.columns:
            return []
        tenant_df = df[df["store_url"] == store_url]
        return tenant_df.to_dict(orient="records")

# ==========================================
# 5. WEBHOOK RELIABILITY & HTTP DISPATCHER
# ==========================================
class WebhookDispatcher:
    def __init__(self):
        self.max_retries = 5
        self.base_backoff = 2.0
        self.timeout = 5.0
        self.endpoint_health: Dict[str, bool] = {m_id: True for m_id in VALID_TENANTS}

    async def dispatch_webhook(self, merchant_id: str, event_type: str, payload: Dict[str, Any], endpoint_url: str, secret_key: str):
        # Semantics: event_id remains constant across all retry attempts (logical business event)
        event_id = f"evt_{uuid.uuid4().hex[:12]}"
        
        event_envelope = {
            "event_id": event_id,
            "event_type": event_type,
            "event_version": "1.0",
            "occurred_at": datetime.now(timezone.utc).isoformat(),
            "merchant_id": merchant_id,
            "entity_type": "product",
            "entity_id": payload.get("sku", "UNKNOWN"),
            "source": f"gold.{event_type.split('.')[0]}",
            "data": payload
        }

        payload_bytes = json.dumps(event_envelope, sort_keys=True).encode('utf-8')
        attempt = 0
        success = False
        err_msg = ""
        last_delivery_id = ""

        while attempt < self.max_retries and not success:
            attempt += 1
            # Semantics: delivery_id changes on every retry attempt (physical transport attempt)
            delivery_id = f"del_{uuid.uuid4().hex[:8]}"
            last_delivery_id = delivery_id
            timestamp_str = str(int(time.time()))

            # Anti-Replay: Bind timestamp directly into the cryptographic signature payload
            signing_payload = f"{timestamp_str}.".encode('utf-8') + payload_bytes
            signature = hmac.new(secret_key.encode('utf-8'), signing_payload, hashlib.sha256).hexdigest()

            headers = {
                "Content-Type": "application/json",
                "X-Webhook-Id": delivery_id,
                "X-Event-Id": event_id,
                "X-Webhook-Timestamp": timestamp_str,
                "X-Webhook-Signature": signature,
                "X-Idempotency-Key": event_id
            }

            try:
                logger.info(f"[Webhook] Executing HTTP POST for Event {event_id} [Attempt {attempt}/{self.max_retries}, Delivery: {delivery_id}] to {endpoint_url}")
                
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(endpoint_url, content=payload_bytes, headers=headers)
                    
                    if 200 <= response.status_code < 300:
                        success = True
                        self.endpoint_health[merchant_id] = True
                        db_store.log_delivery(delivery_id, event_id, merchant_id, event_type, "SUCCESS", attempt)
                        logger.info(f"[Webhook] Successfully delivered {delivery_id} with status {response.status_code}")
                    else:
                        err_msg = f"HTTP Error Status: {response.status_code} - {response.text}"
                        logger.warning(f"[Webhook] Delivery failed for {delivery_id}: {err_msg}")
            
            except httpx.TimeoutException:
                err_msg = f"Request timed out after {self.timeout}s"
                logger.warning(f"[Webhook] Delivery timeout for {delivery_id}")
            except httpx.RequestError as e:
                err_msg = f"Network connection error: {str(e)}"
                logger.warning(f"[Webhook] Network failure for {delivery_id}: {err_msg}")
            except Exception as e:
                err_msg = str(e)
                logger.warning(f"[Webhook] Unexpected error for {delivery_id}: {err_msg}")

            if not success:
                if attempt == self.max_retries:
                    self.endpoint_health[merchant_id] = False
                    db_store.add_to_dlq(event_id, delivery_id, merchant_id, event_type, event_envelope, err_msg)
                    db_store.log_delivery(delivery_id, event_id, merchant_id, event_type, "DEAD_LETTER", attempt, err_msg)
                else:
                    backoff = self.base_backoff * (2 ** (attempt - 1))
                    jitter = random.uniform(0.1, 1.0)
                    sleep_time = backoff + jitter
                    logger.info(f"[Webhook] Retrying in {sleep_time:.2f} seconds...")
                    await asyncio.sleep(sleep_time)

webhook_engine = WebhookDispatcher()

# ==========================================
# 6. API ENDPOINTS
# ==========================================

@app.get("/")
def read_root():
    return {"message": "Shopify Merchants Serving API is running v2.4.4"}

@app.get("/api/v1/merchants/{merchant_id}/pricing-opportunities")
def get_pricing_opportunities(merchant_id: str, x_api_key: str = Header(...)):
    tenant = verify_tenant_access(merchant_id, x_api_key)
    records = ParquetStoreReader.read_product_data("product_pricing_opportunities", tenant["store_url"])
    return {"merchant_id": merchant_id, "store_url": tenant["store_url"], "record_count": len(records), "data": records}

@app.get("/api/v1/merchants/{merchant_id}/inventory-risks")
def get_inventory_risks(merchant_id: str, x_api_key: str = Header(...)):
    tenant = verify_tenant_access(merchant_id, x_api_key)
    records = ParquetStoreReader.read_product_data("inventory_risk", tenant["store_url"])
    return {"merchant_id": merchant_id, "store_url": tenant["store_url"], "record_count": len(records), "data": records}

@app.get("/api/v1/merchants/{merchant_id}/discount-opportunities")
def get_discount_opportunities(merchant_id: str, x_api_key: str = Header(...)):
    tenant = verify_tenant_access(merchant_id, x_api_key)
    records = ParquetStoreReader.read_product_data("discount_opportunities", tenant["store_url"])
    return {"merchant_id": merchant_id, "store_url": tenant["store_url"], "record_count": len(records), "data": records}

@app.get("/api/v1/merchants/{merchant_id}/competitive-intelligence")
def get_competitive_intelligence(merchant_id: str, x_api_key: str = Header(...)):
    tenant = verify_tenant_access(merchant_id, x_api_key)
    records = ParquetStoreReader.read_product_data("competitive_intelligence", tenant["store_url"])
    return {"merchant_id": merchant_id, "store_url": tenant["store_url"], "record_count": len(records), "data": records}

@app.get("/api/v1/merchants/{merchant_id}/health")
def get_tenant_health(merchant_id: str, x_api_key: str = Header(...)):
    tenant = verify_tenant_access(merchant_id, x_api_key)
    return {"merchant_id": merchant_id, "endpoint_healthy": webhook_engine.endpoint_health.get(merchant_id, True)}

@app.post("/api/v1/webhooks/trigger-test-event")
async def trigger_test_event(merchant_id: str, event_type: str, background_tasks: BackgroundTasks, x_api_key: str = Header(...)):
    tenant = verify_tenant_access(merchant_id, x_api_key)
    mock_payload = {"sku": "SAMPLE-SUPP-01", "message": f"Triggered business event: {event_type}"}
    
    background_tasks.add_task(
        webhook_engine.dispatch_webhook,
        merchant_id=merchant_id,
        event_type=event_type,
        payload=mock_payload,
        endpoint_url=tenant["webhook_endpoint"],
        secret_key=tenant["webhook_secret"]
    )
    return {"status": "QUEUED", "event_type": event_type, "merchant_id": merchant_id}

# ==========================================
# 7. OPERATOR / ADMIN PLANE (SECURED)
# ==========================================
@app.get("/api/v1/internal/system/webhook-logs")
def get_webhook_logs(x_api_key: str = Header(...)):
    admin_key = os.environ.get("ADMIN_API_KEY", "admin_secret_master")
    if not hmac.compare_digest(admin_key.encode('utf-8'), x_api_key.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Unauthorized operator access.")
    
    dlq_items = db_store.get_dlq()
    logs_items = db_store.get_logs(50)
    return {
        "active_dead_letter_count": len(dlq_items),
        "dead_letter_queue": dlq_items,
        "recent_delivery_logs": logs_items
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("Merchants_serving:app", host="127.0.0.1", port=8000, reload=True)