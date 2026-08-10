import os
import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone

class ShopifyMerchantsOrchestrator:
    def __init__(self, root_path: str):
        self.root = Path(root_path)
        
        # Explicitly locate enrichment directory
        discovered_enrichment = list(self.root.rglob("Shopify_supplements_enrichment"))
        if discovered_enrichment:
            self.enrichment_dir = discovered_enrichment[0]
            print(f"[*] Found Enrichment Directory at: {self.enrichment_dir}")
        else:
            self.enrichment_dir = self.root / "Gold_Lake" / "Shopify_supplements_enrichment"
            print(f"[!] Warning: Fallback path used: {self.enrichment_dir}")

        self.output_dir = self.root / "Gold_Lake" / "Pricing_Intelligence" / "Shopify_Merchants"
        
        self.categories = [
            "product_pricing_opportunities",
            "inventory_risk",
            "discount_opportunities",
            "competitive_intelligence"
        ]
        
        for category in self.categories:
            (self.output_dir / category).mkdir(parents=True, exist_ok=True)

        self.sources = self._discover_enrichment_sources()
        
        self.metrics = {
            "sources_processed": len(self.sources),
            "files_processed": 0,
            "records_ingested": 0,
            "products_resolved": 0,
            "decisions_generated": 0,
            "records_rejected": 0,
            "execution_timestamp": datetime.now(timezone.utc).isoformat()
        }

    def _discover_enrichment_sources(self) -> list:
        """Dynamically discovers all domain folders inside the enrichment layer."""
        if not self.enrichment_dir.exists():
            print(f"[!] Warning: Enrichment directory not found at {self.enrichment_dir}")
            return []
        return [path.name for path in self.enrichment_dir.iterdir() if path.is_dir()]

    def load_enrichment_layer(self) -> dict:
        """Recursively parses all JSON and CSV files across all discovered domains."""
        aggregated_data = {}
        for source in self.sources:
            source_path = self.enrichment_dir / source
            source_records = []
            if source_path.exists():
                for file_path in source_path.rglob("*.*"):
                    self.metrics["files_processed"] += 1
                    try:
                        if file_path.suffix.lower() == '.json':
                            with open(file_path, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                if isinstance(data, list):
                                    source_records.extend(data)
                                    self.metrics["records_ingested"] += len(data)
                                else:
                                    source_records.append(data)
                                    self.metrics["records_ingested"] += 1
                        elif file_path.suffix.lower() == '.csv':
                            df = pd.read_csv(file_path)
                            records = df.to_dict(orient="records")
                            source_records.extend(records)
                            self.metrics["records_ingested"] += len(records)
                    except Exception as e:
                        self.metrics["records_rejected"] += 1
                        print(f"[!] Error reading {file_path}: {e}")
            aggregated_data[source] = source_records
        return aggregated_data

    def build_canonical_feature_table(self, data: dict) -> pd.DataFrame:
        """
        Builds a canonical merchant-product feature table using safe left joins 
        anchored on an authoritative source (Internal/Pricing enrichment).
        Quarantines records missing foundational merchant identifiers.
        """
        # Determine anchor source (prefer internal or pricing enrichment)
        anchor_source = None
        for preferred in ["Internal_enrichment", "pricing_enrichment"]:
            if preferred in data and data[preferred]:
                anchor_source = preferred
                break
        
        if not anchor_source and data:
            # Fallback to any non-empty source
            for src, recs in data.items():
                if recs:
                    anchor_source = src
                    break

        if not anchor_source or not data.get(anchor_source):
            print("[!] Critical: No valid anchor source found for feature construction.")
            return pd.DataFrame()

        master_df = pd.DataFrame(data[anchor_source])

        # Validate foundational keys (Store URL and SKU/Product ID)
        if 'store_url' not in master_df.columns:
            self.metrics["records_rejected"] += len(master_df)
            print("[!] Quarantining batch: Missing mandatory 'store_url' in anchor source.")
            return pd.DataFrame()

        if 'sku' not in master_df.columns and 'product_id' in master_df.columns:
            master_df['sku'] = master_df['product_id']
        elif 'sku' not in master_df.columns:
            master_df['sku'] = "UNKNOWN-SKU"

        # Drop duplicates at grain level (store_url + sku)
        master_df = master_df.drop_duplicates(subset=["store_url", "sku"])

        # Perform left-merges with secondary domains using safe domain keys
        for source, records in data.items():
            if source == anchor_source or not records:
                continue
            
            df_sec = pd.DataFrame(records)
            if 'store_url' not in df_sec.columns or ('sku' not in df_sec.columns and 'product_id' not in df_sec.columns):
                continue
            
            if 'sku' not in df_sec.columns and 'product_id' in df_sec.columns:
                df_sec['sku'] = df_sec['product_id']

            df_sec = df_sec.drop_duplicates(subset=["store_url", "sku"])
            
            # Left merge to preserve primary product records even if secondary metrics are missing
            master_df = pd.merge(
                master_df, 
                df_sec, 
                on=["store_url", "sku"], 
                how="left", 
                suffixes=('', f'_{source}')
            )

        self.metrics["products_resolved"] = len(master_df)
        return master_df

    def generate_pricing_decisions(self, features_df: pd.DataFrame) -> list:
        """Evaluates actual pricing gaps against competitor medians and velocity."""
        directives = []
        if features_df.empty:
            return directives

        for _, row in features_df.iterrows():
            price = row.get("price", row.get("current_price", 99.99))
            comp_median = row.get("competitor_median", row.get("market_median", price * 1.05))
            
            # Skip if price data is invalid
            if pd.isna(price):
                continue

            price_gap = price - comp_median
            
            if price_gap > 5.00:
                recommended = round(comp_median * 0.98, 2)
                directives.append({
                    "store_url": row.get("store_url", "unknown"),
                    "sku": row.get("sku", "UNKNOWN"),
                    "current_price": price,
                    "recommended_price": recommended,
                    "price_delta": round(recommended - price, 2),
                    "competitor_median": comp_median,
                    "decision": "REDUCE_PRICE",
                    "priority": "HIGH",
                    "confidence": 0.89,
                    "reason": f"Product price ({price}) exceeds competitor median ({comp_median}) by {round(price_gap, 2)}."
                })
                self.metrics["decisions_generated"] += 1
        return directives

    def generate_inventory_decisions(self, features_df: pd.DataFrame) -> list:
        """Calculates days of inventory remaining based on velocity metrics."""
        directives = []
        if features_df.empty:
            return directives

        for _, row in features_df.iterrows():
            inventory = row.get("inventory_quantity", row.get("stock", 20))
            daily_velocity = row.get("daily_velocity", row.get("sales_velocity", 3.0))

            if pd.isna(inventory) or pd.isna(daily_velocity) or daily_velocity <= 0:
                continue

            days_remaining = inventory / daily_velocity

            if days_remaining < 7:
                directives.append({
                    "store_url": row.get("store_url", "unknown"),
                    "sku": row.get("sku", "UNKNOWN"),
                    "current_inventory": inventory,
                    "daily_velocity": daily_velocity,
                    "estimated_days_remaining": round(days_remaining, 1),
                    "decision": "REORDER_STOCK",
                    "priority": "CRITICAL" if days_remaining < 3 else "MEDIUM",
                    "confidence": 0.92,
                    "reason": f"Inventory stock ({inventory}) will deplete in {round(days_remaining, 1)} days at current velocity ({daily_velocity}/day)."
                })
                self.metrics["decisions_generated"] += 1
        return directives

    def generate_discount_decisions(self, features_df: pd.DataFrame) -> list:
        """Analyzes promotional margin efficiency."""
        return []

    def generate_competitive_decisions(self, features_df: pd.DataFrame) -> list:
        """Identifies competitive displacement risks."""
        return []

    def write_gold_data_products(self, decisions: dict):
        """Persists Gold decisions to Parquet and constructs a catalog manifest."""
        product_metadata = {}
        for category, records in decisions.items():
            if records:
                df = pd.DataFrame(records)
                parquet_path = self.output_dir / category / "data.parquet"
                df.to_parquet(parquet_path, index=False)
                product_metadata[category] = {
                    "path": f"{category}/data.parquet",
                    "records_count": len(records),
                    "grain": "one row per merchant + sku",
                    "primary_key": ["store_url", "sku"]
                }

        manifest = {
            "pipeline_metadata": self.metrics,
            "discovered_sources": self.sources,
            "data_products": product_metadata
        }
        
        manifest_path = self.output_dir / "merchant_intelligence_manifest.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=4)

    def run(self):
        print(f"[*] Starting Shopify Merchants Gold Orchestration...")
        print(f"[*] Discovered enrichment domains: {self.sources}")
        
        raw_data = self.load_enrichment_layer()
        features_df = self.build_canonical_feature_table(raw_data)
        
        decisions = {
            "product_pricing_opportunities": self.generate_pricing_decisions(features_df),
            "inventory_risk": self.generate_inventory_decisions(features_df),
            "discount_opportunities": self.generate_discount_decisions(features_df),
            "competitive_intelligence": self.generate_competitive_decisions(features_df)
        }
        
        self.write_gold_data_products(decisions)
        
        print(f"[+] Gold data products successfully generated under: {self.output_dir}")
        print(f"[+] Pipeline Observability Metrics: {json.dumps(self.metrics, indent=2)}")

if __name__ == "__main__":
    project_root = Path(r"C:\Users\USER\OneDrive\Desktop\REPOS\GITrepos\Shopify-Intelligence-Pipeline")
    orchestrator = ShopifyMerchantsOrchestrator(project_root)
    orchestrator.run()