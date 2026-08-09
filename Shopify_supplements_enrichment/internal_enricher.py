import os
import json
import sqlite3
import pandas as pd
from pathlib import Path

def run_internal_enrichment():
    print("[*] Initializing Internal Enrichment Pipeline...")
    
    root_dir = Path(__file__).resolve().parent.parent
    json_path = root_dir / "shopify_supplement_intelligence.json"
    db_path = root_dir / "shopify_intelligence.db"
    
    enrichment_base = root_dir / "shopify_supplements_enrichment"
    pricing_dir = enrichment_base / "pricing_enrichment"
    discount_dir = enrichment_base / "discount_enrichment"
    inventory_dir = enrichment_base / "inventory_enrichment"
    
    for d in [pricing_dir, discount_dir, inventory_dir]:
        d.mkdir(parents=True, exist_ok=True)
        
    if not json_path.exists() or not db_path.exists():
        print("[!] Error: Required source files (JSON or SQLite DB) not found.")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        raw_json_data = json.load(f)
        
    conn = sqlite3.connect(db_path)
    historical_df = pd.read_sql_query("SELECT * FROM product_snapshots", conn)
    conn.close()
    
    print(f"[+] Loaded {len(raw_json_data)} active JSON records and {len(historical_df)} historical snapshot rows.")

    # 1. Pricing & Volatility Enrichment
    print("[*] Computing Pricing Enrichments...")
    if not historical_df.empty and "sku" in historical_df.columns:
        price_agg = historical_df.groupby(["sku", "product_title", "store_url"]).agg(
            current_price=("price", "last"),
            previous_price=("price", "first"),
            mean_price=("price", "mean"),
            min_recorded_price=("price", "min"),
            max_recorded_price=("price", "max"),
            price_observation_count=("price", "count")
        ).reset_index()
        
        price_agg["price_change"] = price_agg["current_price"] - price_agg["previous_price"]
        price_agg["price_change_percentage"] = (
            (price_agg["price_change"] / price_agg["previous_price"]) * 100
        ).fillna(0.0).round(2)
        price_agg["price_volatility_spread"] = price_agg["max_recorded_price"] - price_agg["min_recorded_price"]
    else:
        price_agg = pd.DataFrame(raw_json_data)
        price_agg["current_price"] = price_agg["price"]
        price_agg["price_change"] = 0.0
        price_agg["price_change_percentage"] = 0.0
        price_agg["price_volatility_spread"] = 0.0

    pricing_output_file = pricing_dir / "price_metrics.json"
    price_agg.to_json(pricing_output_file, orient="records", indent=4)
    print(f"[✔] Pricing enrichments exported to {pricing_output_file}")

    # 2. Discount & Bundle Enrichment
    print("[*] Computing Discount & Bundle Enrichments...")
    discount_records = []
    bundle_keywords = ["bundle", "stack", "kit", "pack", "+ free", "system"]
    
    for item in raw_json_data:
        title = str(item.get("product_title", "")).lower()
        sku = str(item.get("sku", "")).lower()
        is_bundle = any(kw in title or kw in sku for kw in bundle_keywords) or "bundle" in str(item.get("product_handle", "")).lower()
        
        price = float(item.get("price", 0.0))
        compare_at = float(item.get("compare_at_price", price))
        discount_spread = max(0.0, compare_at - price)
        discount_percentage = (discount_spread / compare_at * 100) if compare_at > 0 else 0.0
        
        enriched_item = item.copy()
        enriched_item["is_bundle"] = is_bundle
        enriched_item["bundle_classification_flag"] = "Bundle/Stack" if is_bundle else "Standard SKU"
        enriched_item["discount_spread"] = round(discount_spread, 2)
        enriched_item["discount_percentage"] = round(discount_percentage, 2)
        discount_records.append(enriched_item)
        
    discount_df = pd.DataFrame(discount_records)
    discount_output_file = discount_dir / "promotion_metrics.json"
    discount_df.to_json(discount_output_file, orient="records", indent=4)
    print(f"[✔] Discount & bundle enrichments exported to {discount_output_file}")

    # 3. Inventory & Velocity Enrichment
    print("[*] Computing Inventory & State Transition Enrichments...")
    if not historical_df.empty and "available" in historical_df.columns:
        inv_agg = historical_df.groupby(["sku", "product_title", "store_url"]).agg(
            total_snapshots=("available", "count"),
            in_stock_count=("available", lambda x: (x == True).sum()),
            out_of_stock_count=("available", lambda x: (x == False).sum()),
            latest_inventory_qty=("inventory_quantity", "last")
        ).reset_index()
        
        inv_agg["availability_rate"] = (inv_agg["in_stock_count"] / inv_agg["total_snapshots"] * 100).round(2)
        inv_agg["stockout_rate"] = (inv_agg["out_of_stock_count"] / inv_agg["total_snapshots"] * 100).round(2)
        inv_agg["supply_chain_status"] = inv_agg["availability_rate"].apply(
            lambda rate: "High Reliability" if rate >= 90 else ("Unstable/Intermittent" if rate >= 50 else "High Stockout Risk")
        )
    else:
        inv_agg = pd.DataFrame(raw_json_data)
        inv_agg["availability_rate"] = 100.0
        inv_agg["stockout_rate"] = 0.0
        inv_agg["supply_chain_status"] = "Unknown State"

    inventory_output_file = inventory_dir / "inventory_metrics.json"
    inv_agg.to_json(inventory_output_file, orient="records", indent=4)
    print(f"[✔] Inventory enrichments exported to {inventory_output_file}")
    
    print("\n[✔] Internal Enrichment Pipeline executed successfully across all subdomains.")

if __name__ == "__main__":
    run_internal_enrichment()
