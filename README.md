<img width="1366" height="768" alt="image" src="https://github.com/user-attachments/assets/1aa8cd56-009c-4864-90f9-cb2417bfcb9b" />
<img width="1366" height="768" alt="image" src="https://github.com/user-attachments/assets/1bf8ff72-a6c1-4262-bc81-9276792f2c2f" />
<img width="1366" height="768" alt="image" src="https://github.com/user-attachments/assets/f3c70472-b96a-4fe3-91d5-c14bdb43e4e9" />
<img width="1366" height="768" alt="image" src="https://github.com/user-attachments/assets/491a4509-4123-4fb2-b62a-2936a5e8c151" />
<img width="1366" height="768" alt="image" src="https://github.com/user-attachments/assets/6634e59f-1e14-4b3a-a514-43716ea54512" />
<img width="1366" height="768" alt="image" src="https://github.com/user-attachments/assets/aa5104db-6bb9-4778-8579-f27a2995d04a" />
<img width="1366" height="768" alt="image" src="https://github.com/user-attachments/assets/20fe8a89-9787-4f94-acb3-6790597a75c3" />


**🚀 Supplement Brand Intelligence Engine (SBIE)**
End-to-End Market & Commercial Intelligence for Shopify Supplement Brands
The Supplement Brand Intelligence Engine (SBIE) is a purpose-built commercial intelligence platform designed specifically for Direct-to-Consumer (DTC) Supplements, Sports Nutrition, and Wellness brands operating on Shopify.

Rather than treating e-commerce monitoring as a generic web-scraping task, SBIE solves the specific domain problems of the supplement industry: flavor and serving-size variant shifts, ingredient-level pricing compression, hidden promotional discounting, and uncoordinated ad spend bursts by competitors.

**🎯 The Real Problem: Fragmented Intelligence in the Supplement Market**
Supplement brands face hyper-competitive pressure with razor-thin margins. Legacy e-commerce tools track simple price tags, but completely fail to capture how supplement products are actually sold and bought.

**Plaintext**
 Competitor Storefronts, Ad Platforms, & Market Signals
                           │
                           ▼
   ❌ Legacy Scrapers & Generic E-Commerce Tools
                           │
 ┌─────────────────────────┴─────────────────────────┐
 │ ❌ Misses Servings vs. Container Size Math        │
 │ ❌ Fails to Track Hidden Sub-and-Save Discounts   │
 │ ❌ Blind to Flavor/Variant Assortment Expansions  │
 │ ❌ No Context Between Price Drops & Paid Ad Drops │
 └─────────────────────────┬─────────────────────────┘
                           ▼
 💸 Reactive Merchandising, Wasted Ad Spend, & Margin Loss
Critical Questions Generic Tools Fail to Answer:
Cost-Per-Serving & Ingredient Arbitrage: "Did a competitor drop their Creatine price, or did they quietly reduce the tub from 60 servings to 45 servings while keeping the MSRP at $29.99?"

Stockout Conquesting: "Which key competitor SKUs (e.g., Grass-Fed Whey Isolate, Unflavored Electroytes) went out of stock today so we can immediately conquest their branded search ads?"

Flavor & Variant Expansion: "What new flavor variants or bundle configurations are top-performing brands launching and backing with heavy paid ad spend?"

Holistic Commercial Context: "Is a competitor's price drop backed by a massive Meta/TikTok creative blitz, declining customer sentiment around 'taste/clumping,' or an organic SEO push?"

🏗️ Domain-Engineered Architecture
SBIE processes raw storefront signals, multi-domain supplement market data, and promotional activity into decision-ready business intelligence.

Plaintext
                ┌────────────────────────────────────────┐
                │   SHOPIFY STOREFRONTS & WEB SOURCES    │
                │  (Nutritional, Active SKUs, Variants)  │
                └───────────────────┬────────────────────┘
                                    │
                                    ▼
                ┌────────────────────────────────────────┐
                │          INGESTION & CAPTURE           │
                │  Async Storefront API & Schema Normal  │
                └───────────────────┬────────────────────┘
                                    │
                                    ▼
                ┌────────────────────────────────────────┐
                │     BRONZE LAKE — Audit & Provenance   │
                │ Raw Storefront State & Historical Evidence │
                └───────────────────┬────────────────────┘
                                    │
                                    ▼
                ┌────────────────────────────────────────┐
                │    SILVER LAKE — Supplement Canonical  │
                │ Servings Normalization, SKU & Variant   │
                │         Identity (SCD Type 2)          │
                └───────────────────┬────────────────────┘
                                    │
                                    ▼
┌───────────────────────────────────────────────────────────────────────┐
│                    SUPPLEMENT ENRICHMENT ENGINE                       │
│  Serving Economics │ Review Sentiment (Taste/Mixability) │ SEO Rank    │
│  Paid Ad Velocity │ Social Reach & Influencer Volume   │ Geo Arbitrage│
└──────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
                ┌────────────────────────────────────────┐
                │     GOLD LAKE — Commercial Cubes       │
                │  Price Drops, Stockout Opportunities,  │
                │       Assortment Gap Analysis          │
                └───────────────────┬────────────────────┘
                                    │
                                    ▼
                ┌────────────────────────────────────────┐
                │       MULTI-TENANT SERVING LAYER       │
                │    FastAPI, Webhooks, Row Isolation    │
                └────────────────────────────────────────┘
💼 Core Intelligence Pipeline Breakdown
🥉 1. Bronze Layer — Raw Market Provenance
Captures and preserves raw, point-in-time storefront state. Ensures complete legal auditability and historical verification of competitor changes over time.

🥈 2. Silver Layer — Supplement Canonical Standard
Transforms raw e-commerce schemas into a normalized data model built around supplement purchasing behavior.

Serving & Size Normalization: Standardizes variants across serving counts, container weights (grams/lbs), and bundle packages.

Longitudinal Tracking (SCD Type 2): Tracks price shifts, compare-at-price adjustments, and hidden unit-economic changes over time.

Data Contracts: Enforces clean separation between single products, multi-packs, and subscription variants.

🧠 3. Supplement Market Enrichment Engine
Enriches product-level observations with 8 essential commercial domains:

Customer Reviews & Sentiment Analysis: Tracks review velocity and specific sentiment clusters critical to nutrition products ("taste," "mixability," "clumping," "stomach distress").

Paid Ad Creative Velocity: Monitors active ad variations across Meta, TikTok, and Google, highlighting long-running, high-converting copy and creative concepts.

SEO & Search Intent: Evaluates organic performance for high-intent supplement keywords (e.g., "grass-fed whey isolate," "sugar-free electrolytes").

Social & Influencer Volume: Measures brand cross-platform traction, viral social coefficients, and influencer channel reach.

Geographical & Currency Arbitrage: Identifies cross-border pricing spreads (USD, GBP, EUR) for brands scaling international exports.

Brand Reputation & Positioning: Benchmarks positioning against direct market tiers (e.g., Premium Clinical, Mass Market, Natural/Organic).

Competitor Similarity Engine: Automatically maps substitute SKUs using vector similarity across formula positioning, ingredients, and target use-cases.

Macro Trend Velocities: Identifies broader category growth trends across emerging active ingredients and dietary callouts.

🥇 4. Gold Layer — Actionable Business Data Products
Exposes high-level data models optimized directly for brand operations:

pricing_opportunities/: Real-time price drops, margin shifts, and unit-economic changes.

inventory_intelligence/: Immediate stockout tracking to trigger targeted ad conquest campaigns.

discount_opportunities/: Promotional cadence, gift-with-purchase (GWP) tracking, and sale cycles.

competitive_intelligence/: Comprehensive multi-signal brand scorecards.

⚡ Multi-Tenant Serving API & Integration
SBIE provides safe, role-based access to commercial intelligence via an asynchronous FastAPI serving layer with tenant isolation.

🔑 Enterprise Security & Isolation
Authentication: Header-based authorization (x-api-key) utilizing constant-time comparison routines to prevent timing exploits.

Strict Tenant Isolation: Data returned is scoped strictly by merchant_id and authorized store domains.

📸 Live Enriched Payload (Supplement Domain Example)
Real-time response delivering canonical product metrics combined with ad intelligence, review sentiment, and organic search position:

JSON
{
  "merchant_id": "transparentlabs",
  "store_url": "https://www.transparentlabs.com",
  "record_count": 289,
  "data": [
    {
      "store_id": "https://www.transparentlabs.com",
      "store_url": "https://www.transparentlabs.com",
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
        "instagram": "https://instagram.com/transparentlabs",
        "tiktok": "https://tiktok.com/@transparentlabs"
      },
      "social_followers_total": 85000
    }
  ]
}
🔄 Real-Time Event Webhook Engine
To convert insights into automated workflows (e.g., automatically adjusting Google Ad spend when a competitor goes out of stock), SBIE provides an event distribution engine:

HMAC-SHA256 Signatures: Cryptographically signed payloads (X-Webhook-Signature) verify sender authenticity.

Automated Retries & Backoff: Retries failed webhook deliveries up to 5 times using exponential backoff with jitter.

Dead-Letter Queue (DLQ): Safely logs unserviceable delivery endpoints for operator review without dropping data.

Idempotency Safeguards: Every event payload carries a unique X-Idempotency-Key to prevent duplicated downstream actions.

🛠️ Repository Layout
Plaintext
.
├── Shopify-Supplements/              # Ingestion Engine
│   ├── pipeline.py                   # End-to-end execution pipeline
│   ├── engine.py                     # Async HTTP/2 storefront capture engine
│   ├── graphql_client.py             # Shopify Storefront GraphQL handler
│   ├── normalizer.py                 # Raw store response normalization
│   ├── db_manager.py                 # Bronze Lake persistence engine
│   └── silver_supplements_orchestrator.py # Bronze to Silver transformer
│
├── shopify_supplements_enrichment/   # Supplement Intelligence Engine
│   ├── pricing_enrichment/           # Serving cost & margin calculations
│   ├── external_enrichment/          # Multi-Domain Market Intelligence
│   │   ├── customer_reviews/         # Taste, mixability & review extraction
│   │   ├── brand_reputation/        # Category tiering & brand scoring
│   │   ├── seo_search/               # Ingredient search volume & rank tracking
│   │   ├── social_engagement/        # Influencer engagement metrics
│   │   ├── ad_intelligence/          # Meta, TikTok & Google ad tracker
│   │   ├── geographical_arbitrage/   # Global cross-border pricing spreads
│   │   ├── competitor_similarity/    # Vector-based formula/SKU mapping
│   │   └── market_trends/            # Category & ingredient growth trends
│   ├── external_enricher.py          # Multi-domain orchestrator
│   └── api_clients.py                # Intelligence gateway integration
│
├── Gold_Lake/                        # Commercial Decision Storage
│   └── Pricing_Intelligence/         # Business-ready Parquet analytical datasets
│
├── app/                              # Commercial Serving Layer
│   ├── main.py                       # FastAPI application & business routes
│   ├── security.py                   # API key security & constant-time validation
│   └── webhooks.py                   # HMAC signing, retry engine & DLQ
│
└── README.md
🧭 Core Design Principles
Merchant Decisions First: Every metric collected must answer an explicit commercial question around pricing, inventory conquesting, or product expansion.

Domain Context Over Raw Data: Raw price changes mean nothing without understanding variant size changes, active paid ad campaigns, and customer review sentiment.

Strict Data Provenance: Every metric is clearly flagged with its origin source: OBSERVED (storefront observations), EXTERNAL (market APIs), or SIMULATED (fallback calculation engines).

Reliability & Data Quality: Focuses on clean deduplication, unit normalization, and verified business schema contracts rather than unvalidated raw volume.
