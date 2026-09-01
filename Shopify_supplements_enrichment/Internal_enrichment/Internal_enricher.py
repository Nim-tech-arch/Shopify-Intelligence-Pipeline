import os
import re
import json
import sqlite3
import hashlib
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any

# ==========================================
# REGEX CONSTANTS & STRUCTURAL MAPPING
# ==========================================
NON_SUPPLEMENT_KEYWORDS = [
    r"\bbra\b", r"\bhat\b", r"\bcap\b", r"\bshirt\b", r"\btee\b", r"\bhoodie\b",
    r"\bjogger\b", r"\bshorts\b", r"\blegging\b", r"\bshaker\b", r"\bbottle\b",
    r"\bstrap\b", r"\bwrap\b", r"\bapparel\b", r"\bgear\b", r"\bslugger\b"
]

INGREDIENT_CONFIG = {
    "caffeine": {"pattern": r"(\d+\.?\d*)\s*(?:mg|milligrams?)\s*(?:of\s*)?caffeine", "unit": "mg"},
    "creatine": {"pattern": r"(\d+\.?\d*)\s*(?:g|grams?)\s*(?:of\s*)?creatine", "unit": "g"},
    "protein": {"pattern": r"(\d+\.?\d*)\s*(?:g|grams?)\s*(?:of\s*)?protein", "unit": "g"},
    "ashwagandha": {"pattern": r"(\d+\.?\d*)\s*(?:mg|milligrams?)\s*(?:of\s*)?ashwagandha", "unit": "mg"},
    "citrulline": {"pattern": r"(\d+\.?\d*)\s*(?:g|grams?)\s*(?:of\s*)?citrulline", "unit": "g"},
    "beta_alanine": {"pattern": r"(\d+\.?\d*)\s*(?:g|grams?)\s*(?:of\s*)?beta[-\s]?alanine", "unit": "g"}
}

DIETARY_FLAGS = {
    "is_vegan": [r"(?<!non-)(?<!not\s)\bvegan\b", r"(?<!non-)(?<!not\s)\bplant[-\s]?based\b"],
    "is_gluten_free": [r"(?<!non-)(?<!not\s)\bgluten[-\s]?free\b", r"\bnon[-\s]?gluten\b"],
    "is_sugar_free": [r"(?<!non-)(?<!not\s)\bsugar[-\s]?free\b", r"\bzero[-\s]?sugar\b", r"\b0g[-\s]?sugar\b"],
    "is_keto": [r"(?<!non-)(?<!not\s)\bketo\b", r"\bketo[-\s]?friendly\b"],
    "is_third_party_tested": [r"\binformed[-\s]?choice\b", r"\bnsf\b", r"\bthird[-\s]?party[-\s]?tested\b"]
}

# ==========================================
# PARSING & ENRICHMENT HELPERS
# ==========================================
def extract_ingredients(text: str) -> List[Dict[str, Any]]:
    ingredients = []
    text_lower = text.lower()
    for ing_name, config in INGREDIENT_CONFIG.items():
        match = re.search(config["pattern"], text_lower)
        if match:
            ingredients.append({
                "name": ing_name,
                "amount": float(match.group(1)),
                "unit": config["unit"]
            })
    return ingredients

def extract_dietary_tags(text: str) -> Dict[str, bool]:
    text_lower = text.lower()
    tags = {}
    for flag_name, patterns in DIETARY_FLAGS.items():
        tags[flag_name] = any(re.search(pat, text_lower) for pat in patterns)
    return tags

def classify_taxonomy(title: str, category_raw: str) -> Dict[str, Any]:
    combined = f"{title} {category_raw}".lower()
    
    # 1. Apparel & Gear Detection
    if any(re.search(pat, combined) for pat in NON_SUPPLEMENT_KEYWORDS):
        return {
            "primary_category": "Apparel & Accessories",
            "subcategory": "Merchandise",
            "is_apparel_or_gear": True
        }
    
    # 2. Supplement Sub-categorization
    if any(k in combined for k in ["protein", "whey", "isolate"]):
        sub = "Protein & Mass"
    elif any(k in combined for k in ["pre-workout", "preworkout", "pump", "energy"]):
        sub = "Pre-Workout"
    elif any(k in combined for k in ["creatine"]):
        sub = "Amino Acids & Creatine"
    elif any(k in combined for k in ["nootropic", "focus", "brain"]):
        sub = "Nootropics & Performance"
    elif any(k in combined for k in ["vitamin", "gummy", "wellness", "health"]):
        sub = "Vitamins & Wellness"
    else:
        sub = "General Supplement"
        
    return {
        "primary_category": "Sports Nutrition & Supplements",
        "subcategory": sub,
        "is_apparel_or_gear": False
    }

def generate_canonical_hash(vendor: str, product_title: str) -> str:
    clean_title = re.sub(r'[^a-zA-Z0-9]', '', product_title.lower())
    clean_vendor = re.sub(r'[^a-zA-Z0-9]', '', vendor.lower())
    raw_str = f"{clean_vendor}:{clean_title}"
    return hashlib.sha256(raw_str.encode('utf-8')).hexdigest()[:16]

# ==========================================
# MAIN INTERNAL ENRICHER ENGINE
# ==========================================
def run_internal_enrichment():
    print("[*] Initializing SIP Internal Enrichment Engine...")
    
    # Dynamic Path Resolution: Resolves to workspace root (Shopify-Intelligence-Pipeline)
    script_dir = Path(__file__).resolve().parent
    root_dir = script_dir.parents[1]  # Steps up two levels to root
    
    # Silver JSON Candidate Paths
    silver_candidates = [
        root_dir / "shopify_supplements_silver.json",
        root_dir / "shopify_supplements_silver" / "shopify_supplements_silver.json",
        script_dir.parent / "shopify_supplements_silver.json",
    ]
    
    silver_json_path = None
    for candidate in silver_candidates:
        if candidate.exists():
            silver_json_path = candidate
            break

    if not silver_json_path:
        print(f"[!] Error: Silver JSON missing under {root_dir}")
        print("Checked paths:")
        for c in silver_candidates:
            print(f"  - {c}")
        return

    print(f"[+] Ingesting Silver JSON from: {silver_json_path}")

    # Output Directory Configuration
    db_path = root_dir / "shopify_intelligence.db"
    enrichment_base = root_dir / "Shopify_supplements_enrichment"
    pricing_dir = enrichment_base / "pricing_enrichment"
    discount_dir = enrichment_base / "discount_enrichment"
    inventory_dir = enrichment_base / "inventory_enrichment"
    gold_dir = root_dir / "Gold_Lake"
    
    for d in [pricing_dir, discount_dir, inventory_dir, gold_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # 1. Load Silver JSON
    with open(silver_json_path, "r", encoding="utf-8") as f:
        silver_data = json.load(f)

    # 2. Extract Longitudinal Snapshots from Database
    historical_agg = {}
    if db_path.exists():
        conn = sqlite3.connect(db_path)
        try:
            hist_df = pd.read_sql_query("SELECT variant_id, price, available FROM product_snapshots", conn)
            if not hist_df.empty:
                grouped = hist_df.groupby("variant_id").agg(
                    mean_historic_price=("price", "mean"),
                    min_historic_price=("price", "min"),
                    max_historic_price=("price", "max"),
                    total_snapshots=("available", "count"),
                    in_stock_snapshots=("available", lambda x: (x == 1).sum())
                ).reset_index()
                
                for _, row in grouped.iterrows():
                    v_id = str(row["variant_id"])
                    total = row["total_snapshots"]
                    avail_rate = round((row["in_stock_snapshots"] / total * 100), 2) if total > 0 else 100.0
                    historical_agg[v_id] = {
                        "mean_historic_price": round(float(row["mean_historic_price"]), 2),
                        "price_volatility_spread": round(float(row["max_historic_price"] - row["min_historic_price"]), 2),
                        "historical_availability_rate": avail_rate
                    }
        except Exception as e:
            print(f"[!] Warning: Could not process product_snapshots: {e}")
        finally:
            conn.close()

    # 3. Calculate Cross-Store Market Baseline
    silver_df = pd.DataFrame(silver_data)
    market_medians = {}
    if not silver_df.empty and "product_title" in silver_df.columns and "price_usd" in silver_df.columns:
        market_medians = silver_df.groupby("product_title")["price_usd"].median().to_dict()

    enriched_records = []
    pricing_metrics = []
    promotion_metrics = []
    inventory_metrics = []

    # 4. Processing Execution Loop
    for item in silver_data:
        p_title = str(item.get("product_title", ""))
        v_title = str(item.get("variant_title", ""))
        vendor = str(item.get("vendor", ""))
        full_text = f"{p_title} {v_title}"
        sku = str(item.get("sku", ""))
        v_id = str(item.get("variant_id", ""))
        
        # Domain 1: Taxonomy & Apparel Filtering
        tax_info = classify_taxonomy(p_title, str(item.get("category", "")))
        
        # Domain 2: Pricing & Value Metrics
        price_usd = float(item.get("price_usd", 0.0))
        compare_at = float(item.get("compare_at_price_usd", price_usd))
        discount_spread = max(0.0, round(compare_at - price_usd, 2))
        discount_pct = round((discount_spread / compare_at * 100), 2) if compare_at > 0 else 0.0
        
        # Domain 3: Unit Economics
        pkg_size_g = float(item.get("package_size_g", 0.0))
        servings = int(item.get("serving_count", 0))
        price_per_g = round(price_usd / pkg_size_g, 4) if pkg_size_g > 0 else 0.0
        price_per_serving = round(price_usd / servings, 2) if servings > 0 else 0.0
        
        # Domain 4: Cross-Store Indexing
        market_median = market_medians.get(p_title, price_usd)
        price_variance_pct = round(((price_usd - market_median) / market_median * 100), 2) if market_median > 0 else 0.0

        # Domain 5: Ingredient Parsing & Dietary Tags
        ingredients = extract_ingredients(full_text)
        dietary_tags = extract_dietary_tags(full_text)
        canonical_hash = generate_canonical_hash(vendor, p_title)

        # Domain 6: Inventory & Historical Signals
        is_in_stock = bool(item.get("is_in_stock", False))
        stock_status = str(item.get("stock_status", "UNKNOWN"))
        qty = int(item.get("inventory_quantity", 0))
        
        hist_data = historical_agg.get(v_id, {
            "mean_historic_price": price_usd,
            "price_volatility_spread": 0.0,
            "historical_availability_rate": 100.0 if is_in_stock else 0.0
        })

        # Domain 7: Brand Health Index
        base_health = 100.0
        if not is_in_stock:
            base_health -= 25.0
        if tax_info["is_apparel_or_gear"]:
            base_health -= 10.0
        data_quality = float(item.get("data_quality_score", 100))
        brand_health_score = max(0.0, round((base_health * 0.7) + (data_quality * 0.3), 2))

        # Build Gold Output Record
        gold_record = item.copy()
        gold_record.update({
            "canonical_product_hash": canonical_hash,
            "primary_category": tax_info["primary_category"],
            "subcategory": tax_info["subcategory"],
            "is_apparel_or_gear": tax_info["is_apparel_or_gear"],
            "discount_spread": discount_spread,
            "discount_pct": discount_pct,
            "price_per_gram_usd": price_per_g,
            "price_per_serving_usd": price_per_serving,
            "market_median_price_usd": market_median,
            "price_variance_vs_market_pct": price_variance_pct,
            "mean_historic_price": hist_data["mean_historic_price"],
            "price_volatility_spread": hist_data["price_volatility_spread"],
            "parsed_ingredients": ingredients,
            "dietary_tags": dietary_tags,
            "brand_health_score": brand_health_score
        })
        
        enriched_records.append(gold_record)
        
        # Sub-domain Exports
        pricing_metrics.append({
            "store_id": item.get("store_id"),
            "product_id": item.get("product_id"),
            "variant_id": v_id,
            "sku": sku,
            "price_usd": price_usd,
            "market_median_price_usd": market_median,
            "price_variance_vs_market_pct": price_variance_pct,
            "mean_historic_price": hist_data["mean_historic_price"],
            "price_volatility_spread": hist_data["price_volatility_spread"],
            "price_per_gram_usd": price_per_g,
            "price_per_serving_usd": price_per_serving
        })
        
        promotion_metrics.append({
            "store_id": item.get("store_id"),
            "variant_id": v_id,
            "product_title": p_title,
            "compare_at_price_usd": compare_at,
            "price_usd": price_usd,
            "discount_spread": discount_spread,
            "discount_pct": discount_pct,
            "is_promotional_gift": item.get("is_promotional_gift", False)
        })
        
        inventory_metrics.append({
            "store_id": item.get("store_id"),
            "variant_id": v_id,
            "stock_status": stock_status,
            "is_in_stock": is_in_stock,
            "inventory_quantity": qty,
            "historical_availability_rate": hist_data["historical_availability_rate"],
            "brand_health_score": brand_health_score
        })

    # 5. Write Artifacts
    pd.DataFrame(pricing_metrics).to_json(pricing_dir / "price_metrics.json", orient="records", indent=4)
    pd.DataFrame(promotion_metrics).to_json(discount_dir / "promotion_metrics.json", orient="records", indent=4)
    pd.DataFrame(inventory_metrics).to_json(inventory_dir / "inventory_metrics.json", orient="records", indent=4)
    
    gold_output_path = gold_dir / "shopify_supplements_gold.json"
    with open(gold_output_path, "w", encoding="utf-8") as f:
        json.dump(enriched_records, f, indent=4)

    print(f"[✔] Successfully processed {len(enriched_records)} records into Gold Lake.")
    print(f"[✔] Pricing Output -> {pricing_dir / 'price_metrics.json'}")
    print(f"[✔] Promotion Output -> {discount_dir / 'promotion_metrics.json'}")
    print(f"[✔] Inventory Output -> {inventory_dir / 'inventory_metrics.json'}")
    print(f"[✔] Lake Output -> {gold_output_path}")

if __name__ == "__main__":
    run_internal_enrichment()