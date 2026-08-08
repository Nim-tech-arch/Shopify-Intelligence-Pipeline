import json
import sqlite3
import hashlib
from datetime import datetime
import pandas as pd
import numpy as np

# Configuration paths - using correct singular JSON filename
BRONZE_JSON = "shopify_supplement_intelligence.json"
BRONZE_DB = "shopify_intelligence_db"
SILVER_DB = "shopify_silver_intelligence.db"
SILVER_JSON = "shopify_supplements_silver.json"

def generate_store_id(store_url: str) -> str:
    """Generate a consistent, deterministic store ID from the store URL."""
    if not store_url:
        return "unknown_store"
    cleaned = store_url.strip().lower().replace("https://", "").replace("http://", "").rstrip("/")
    return hashlib.md5(cleaned.encode()).hexdigest()[:12]

def compute_data_quality_score(row) -> float:
    """Calculate a data quality score (0.0 to 1.0) based on field completeness."""
    critical_fields = [
        row.get("store_id"),
        row.get("product_id"),
        row.get("product_title"),
        row.get("price"),
        row.get("vendor"),
        row.get("product_url"),
        row.get("image_url")
    ]
    score = sum(1 for f in critical_fields if pd.notnull(f) and str(f).strip() != "" and str(f).lower() != "nan")
    return round(score / len(critical_fields), 4)

def run_silver_orchestrator():
    print("[*] Initializing Silver Layer Orchestration...")

    df = pd.DataFrame()

    # 1. Ingest Bronze Data from JSON
    try:
        with open(BRONZE_JSON, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
        df = pd.DataFrame(raw_data)
        print(f"[+] Loaded {len(df)} records from Bronze JSON: {BRONZE_JSON}")
    except FileNotFoundError:
        print(f"[-] JSON file '{BRONZE_JSON}' not found. Attempting to query SQLite DB...")
        try:
            conn = sqlite3.connect(BRONZE_DB)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            print(f"[*] Available SQLite tables: {tables}")
            
            if not tables:
                raise ValueError("No tables found in SQLite database.")
            
            target_table = tables[0]
            print(f"[+] Querying table: {target_table}")
            df = pd.read_sql(f"SELECT * FROM {target_table}", conn)
            conn.close()
            print(f"[+] Loaded {len(df)} records from SQLite database.")
        except Exception as e:
            print(f"[-] Failed to load from SQLite DB: {e}")

    if df.empty:
        print("[!] No records found in Bronze layer. Exiting pipeline.")
        return

    # 2. Standardization & Schema Projection
    print("[*] Applying schema conformation and standardizing fields...")
    
    expected_cols = ['store_url', 'product_title', 'price', 'compare_at_price', 'vendor', 
                     'product_id', 'product_handle', 'variants', 'crawl_timestamp', 'product_type', 
                     'product_url', 'image_url', 'availability', 'inventory_status']
    for col in expected_cols:
        if col not in df.columns:
            df[col] = None

    # Clean text fields
    df['product_title'] = df['product_title'].astype(str).str.strip()
    df['vendor'] = df['vendor'].fillna("Unknown Vendor").astype(str).str.strip()
    df['product_handle'] = df['product_handle'].astype(str).str.strip()
    df['store_url'] = df['store_url'].astype(str).str.strip()

    # Generate Store ID
    df['store_id'] = df['store_url'].apply(generate_store_id)

    # 3. Price & Discount Normalization
    df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0.0)
    df['compare_at_price'] = pd.to_numeric(df['compare_at_price'], errors='coerce').fillna(0.0)
    
    df['currency'] = "USD"

    mask_discount = df['compare_at_price'] > df['price']
    df['discount_amount'] = 0.0
    df['discount_percentage'] = 0.0
    
    df.loc[mask_discount, 'discount_amount'] = (df['compare_at_price'] - df['price']).round(2)
    df.loc[mask_discount, 'discount_percentage'] = ((df['discount_amount'] / df['compare_at_price']) * 100).round(2)

    # 4. Variant and Inventory Normalization
    def parse_variant_count(v):
        if isinstance(v, list):
            return len(v)
        elif isinstance(v, str) and v.startswith('['):
            try:
                parsed = json.loads(v)
                return len(parsed) if isinstance(parsed, list) else 1
            except:
                return 1
        return 1

    df['variant_count'] = df['variants'].apply(parse_variant_count)
    df['availability'] = df['availability'].fillna(True).astype(bool)
    df['inventory_status'] = df['availability'].apply(lambda x: "IN_STOCK" if x else "OUT_OF_STOCK")

    # 5. Timestamping & Historical Tracking
    from datetime import timezone

current_time = datetime.now(timezone.utc).isoformat()
    df['crawl_timestamp'] = pd.to_datetime(df['crawl_timestamp'], errors='coerce').fillna(pd.to_datetime(current_time))
    
    df['first_seen_at'] = df['crawl_timestamp']
    df['last_seen_at'] = df['crawl_timestamp']

    # 6. Deduplication & Identity Resolution
    print("[*] Performing deduplication and product identity resolution...")
    df = df.drop_duplicates(subset=['store_id', 'product_id', 'product_handle'], keep='last')

    # 7. Data Quality Scoring
    print("[*] Computing Data Quality Scores...")
    df['data_quality_score'] = df.apply(compute_data_quality_score, axis=1)

    # 8. Project Target Silver Schema Order
    silver_schema_columns = [
        'store_id',
        'store_url',
        'product_id',
        'product_title',
        'product_handle',
        'vendor',
        'product_type',
        'price',
        'compare_at_price',
        'currency',
        'discount_amount',
        'discount_percentage',
        'variant_count',
        'availability',
        'inventory_status',
        'product_url',
        'image_url',
        'crawl_timestamp',
        'first_seen_at',
        'last_seen_at',
        'data_quality_score'
    ]

    silver_df = df[silver_schema_columns].copy()

    silver_df['crawl_timestamp'] = silver_df['crawl_timestamp'].astype(str)
    silver_df['first_seen_at'] = silver_df['first_seen_at'].astype(str)
    silver_df['last_seen_at'] = silver_df['last_seen_at'].astype(str)

    # 9. Persistence
    print(f"[*] Persisting {len(silver_df)} conformed records to Silver storage...")
    
    conn_silver = sqlite3.connect(SILVER_DB)
    silver_df.to_sql("silver_products", conn_silver, if_exists="replace", index=False)
    conn_silver.close()

    silver_df.to_json(SILVER_JSON, orient="records", indent=4)

    print(f"[✔] Silver Layer Orchestration Complete. Output saved to {SILVER_DB} & {SILVER_JSON}")

if __name__ == "__main__":
    run_silver_orchestrator()