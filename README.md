# 🚀 Shopify Intelligence Pipeline (SIP)

## Production-Grade Commercial Intelligence for Direct-to-Consumer (DTC) Brands

The **Shopify Intelligence Pipeline (SIP)** is an enterprise end-to-end data platform that transforms fragmented e-commerce activity, pricing volatility, and multi-channel market signals into structured, historical, and decision-ready commercial intelligence.

Designed specifically for hyper-competitive e-commerce verticals—starting with **Supplements & Sports Nutrition**—SIP continuously monitors competitor storefronts and enriches raw observations with external market signals. It bridges the gap between raw web extraction and actionable business decisions by exposing a multi-tenant, event-driven FastAPI serving layer.

---

## 🎯 The Real Problem: The Blind Spot of E-Commerce Dynamics

E-commerce brands lose millions annually to **unseen competitor moves** and **siloed market signals**. Brand managers, pricing strategists, and merchandising teams routinely face critical operational friction:

```text
  Competitor Storefronts & External Web Signals
                       │
                       ▼
          Manual Observation & Scraping
                       │
                       ▼
  ❌ No Historical Audit Trail / Point-in-Time State
  ❌ Inability to Measure Real-Time Volatility
  ❌ Lack of External Context (Ads, Sentiment, SEO)
  ❌ Blind Reactive Pricing & Merchandising
The Questions Current E-Commerce Tools Fail to Answer:
Pricing & Margin Pressure: "Which competitors silently dropped prices or altered discount margins in the last 24 hours?"

Inventory & Out-of-Stock Arbitrage: "Which high-demand competitor SKUs are currently out of stock, presenting an immediate ad-spend opportunity?"

Assortment Gaps: "Which flavor/size variants are competitors expanding into before market saturation occurs?"

Holistic Intelligence: "Is a competitor's price drop backed by paid ad acceleration, declining customer sentiment, or organic search dominance?"

🏗️ Architectural Topology: Medallion + Enrichment + Serving
SIP processes millions of raw signals into trusted analytical data products using a Medallion Data Architecture (Bronze → Silver → Gold) extended with multi-domain enrichment and secure multi-tenant API serving.

Plaintext
               ┌────────────────────────────────────────┐
               │    SHOPIFY STOREFRONTS & WEB SOURCES   │
               └───────────────────┬────────────────────┘
                                   │
                                   ▼
               ┌────────────────────────────────────────┐
               │         INGESTION (Async HTTP/2)       │
               │   GraphQL / Storefront API / Fallback   │
               └───────────────────┬────────────────────┘
                                   │
                                   ▼
               ┌────────────────────────────────────────┐
               │        BRONZE DATA LAKE (Raw)          │
               │ Immutable payload preserving evidence  │
               └───────────────────┬────────────────────┘
                                   │
                                   ▼
               ┌────────────────────────────────────────┐
               │     SILVER DATA LAKE (Canonical)       │
               │   Deduplicated, Schema-Enforced, SCD2   │
               └───────────────────┬────────────────────┘
                                   │
                                   ▼
┌───────────────────────────────────────────────────────────────────────┐
│                          ENRICHMENT LAYER                             │
│   Pricing Metrics │ Sentiment & Reviews │ SEO & Organic Visibility    │
│   Paid Ad Spends  │ Social Engagement   │ Geo & Currency Arbitrage    │
└──────────────────────────────────┬────────────────────────────────────┘
                                   │
                                   ▼
               ┌────────────────────────────────────────┐
               │        GOLD DATA LAKE (Decision)       │
               │     Parquet Analytic Cubes & Models    │
               └───────────────────┬────────────────────┘
                                   │
                                   ▼
               ┌────────────────────────────────────────┐
               │        MULTI-TENANT SERVING API        │
               │ FastAPI, HMAC Webhooks, Row Isolation  │
               └────────────────────────────────────────┘
💼 End-to-End Pipeline Breakdown
🥉 1. Bronze Layer — Raw Evidence Preservation
Preserves raw HTTP/GraphQL JSON payloads directly from target storefronts without modification. This guarantees absolute data lineage, auditability, and replay capability.

Key Fields: store_url, crawl_timestamp, source_endpoint, crawl_id, raw_payload.

🥈 2. Silver Layer — Canonical E-Commerce Standard
Transforms heterogeneous, volatile storefront schemas into a unified, clean analytical contract.

Deduplication & Data Integrity: Implements strict identity matching across SKUs and variant IDs to prevent metrics inflation.

Product Snapshots: Converts point-in-time observations into longitudinal historical trends (Slowly Changing Dimensions).

Data Schema:

Store (store_id, domain, crawl_timestamp)

Product (product_id, title, handle, vendor, product_type)

Variant (variant_id, sku, price, compare_at_price, available, inventory_quantity)

🧠 3. Enrichment Engine — Multi-Domain Context
Anchors internal canonical products to 8 external intelligence domains to convert price points into commercial context:

Customer Reviews & Sentiment: Analyzes review ratings and customer key-phrase sentiment (e.g., taste, delivery).

Brand Reputation & Market Positioning: Benchmarks relative market authority and tier placement.

SEO & Search Visibility: Captures organic target keyword rankings, search volume, and transaction intent.

Social Engagement: Monitors cross-platform reach, viral coefficients, and social volume.

Paid Ad Intelligence: Tracks active creative counts, platforms (Meta, TikTok, Google), and longest-running ad copy.

Geographical & Currency Arbitrage: Analyzes multi-region pricing spreads (USD, GBP, EUR) for export positioning.

Cross-Brand Benchmarking: Identifies direct functional competitors using vector/attribute similarity.

Market Trend Velocities: Models macro demand changes across product categories.

🥇 4. Gold Layer — Business-Ready Data Products
Aggregates enriched signals into highly optimized Parquet files structured around core merchant workflows:

competitive_pricing/: Price drops, margin compression, relative position.

inventory_intelligence/: Stockout tracking, inventory risk factors.

discount_opportunities/: Historical promotional trends and discount cadence.

competitive_intelligence/: Multi-signal brand scorecards.

⚡ Production Serving Layer & API Integration
SIP provides enterprise-grade data access via an asynchronous, multi-tenant FastAPI serving architecture running over uvicorn.

🔑 Security & Tenant Data Isolation
Authentication: API Key header validation (x-api-key) enforced via constant-time comparison algorithms to eliminate timing attacks.

Row-Level Isolation: Data responses are strictly isolated by merchant_id and verified against authorized tenant store URLs (store_url).

📸 OpenAPI Interface & Verification Screenshots
1. API Key Header Authorization Modal (x-api-key)
Authentication is strictly guarded via HTTP headers across all protected route endpoints.

2. Verified Active Session State
Confirmation of an authorized tenant session displaying an active header credential.

3. Core Operational Intelligence Endpoints
Exposes structured analytics categories including Pricing, Inventory, Sentiment, SEO, Paid Ads, and Corporate Intelligence.

4. Interactive Endpoint Catalog
Full OpenAPI documentation breakdown covering multi-domain analytical routes.

5. Pricing Opportunities Endpoint Execution (GET /api/v1/merchants/{merchant_id}/pricing-opportunities)
Interactive interface allowing merchants to query pricing variance, market medians, and unit economic benchmarks.

6. Live Enriched Response Payload
Real-time API response serving canonical product records enriched with multi-platform ad spend, organic visibility index, customer sentiment, and social metrics.

JSON
{
  "merchant_id": "transparentlabs",
  "store_url": "[https://www.transparentlabs.com](https://www.transparentlabs.com)",
  "record_count": 289,
  "data": [
    {
      "store_id": "[https://www.transparentlabs.com](https://www.transparentlabs.com)",
      "store_url": "[https://www.transparentlabs.com](https://www.transparentlabs.com)",
      "crawl_timestamp": "2026-09-01T07:31:31Z",
      "product_id": 11675265292,
      "variant_id": 39945573662813,
      "product_title": "ZMO",
      "variant_title": "30 Servings",
      "sku": "TL-017404",
      "sentiment_score_positive": 0.88,
      "sentiment_score_negative": 0.12,
      "review_widget_provider": "Judge.me",
      "top_review_keywords": [
        "taste",
        "energy",
        "fast delivery"
      ],
      "target_keyword": "grass-fed whey protein isolate",
      "monthly_search_volume": 8400,
      "organic_rank_position": 4,
      "search_intent": "TRANSACTIONAL",
      "organic_visibility_index": 78.5,
      "has_active_ads": true,
      "active_creative_count": 24,
      "ad_platforms": [
        "Meta",
        "TikTok",
        "Google Search"
      ],
      "longest_running_ad_days": 112,
      "brand_country_of_origin": "USA",
      "estimated_monthly_traffic": 250000,
      "market_segment": "PREMIUM_SPORTS_NUTRITION",
      "social_links": {
        "instagram": "[https://instagram.com/transparentlabs](https://instagram.com/transparentlabs)",
        "tiktok": "[https://tiktok.com/@transparentlabs](https://tiktok.com/@transparentlabs)"
      },
      "social_followers_total": 85000
    }
  ]
}
🔄 Event-Driven Webhook System
To enable immediate action without continuous polling, SIP incorporates an outbound event distribution engine:

HMAC-SHA256 Signing: Every outgoing webhook payload is cryptographically signed using a shared secret and passed via X-Webhook-Signature.

Reliability Guarantees:

Exponential Backoff & Jitter: Retries failed deliveries up to 5 attempts with randomized backoff.

Dead-Letter Queue (DLQ): Failed attempts exceeding maximum retries are logged to an operational DLQ for operator analysis.

Idempotency Keys: Every event carries a unique X-Idempotency-Key to prevent duplicate processing downstream.

🛠️ Repository Layout
Plaintext
.
├── Shopify-Supplements/              # Core Ingestion Engine
│   ├── pipeline.py                  # End-to-end crawl pipeline
│   ├── engine.py                    # Async HTTP/2 crawler execution engine
│   ├── graphql_client.py            # Shopify Storefront GraphQL handler
│   ├── normalizer.py               # Raw response transformation
│   ├── db_manager.py               # SQLite / Bronze lake persistence
│   └── silver_supplements_orchestrator.py # Bronze -> Silver orchestrator
│
├── shopify_supplements_enrichment/  # Enrichment Engine
│   ├── pricing_enrichment/          # Price metrics & baseline calculation
│   ├── external_enrichment/         # 8 Domain intelligence assets (JSON)
│   │   ├── customer_reviews/
│   │   ├── brand_reputation/
│   │   ├── seo_search/
│   │   ├── social_engagement/
│   │   ├── ad_intelligence/
│   │   ├── geographical_arbitrage/
│   │   ├── competitor_similarity/
│   │   └── market_trends/
│   ├── external_enricher.py         # Multi-domain enrichment orchestrator
│   └── api_clients.py               # External API abstraction gateway
│
├── Gold_Lake/                       # Decision-Ready Storage
│   └── Pricing_Intelligence/        # Standardized Parquet data products
│
├── app/                             # FastAPI Serving Architecture
│   ├── main.py                      # FastAPI application & route definitions
│   ├── security.py                  # API key validation & constant-time checks
│   └── webhooks.py                  # HMAC signing, retry, & DLQ engine
│
└── README.md
🧭 Core Design Principles
Business Outcome First: Data acquisition serves specific merchant decisions (e.g., pricing, inventory conquesting).

Raw Evidence Preservation: Source data is immutable in Bronze for total auditability.

Explicit Data Provenance: The system explicitly tags every metric as OBSERVED (real crawl data), EXTERNAL (live API), or SIMULATED (fallback engine).

Reliability Over Vanity Metrics: Prioritizes strict data deduplication and schema validity over raw volume.