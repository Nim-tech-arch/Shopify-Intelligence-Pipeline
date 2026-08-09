# Shopify Intelligence Pipeline

## From Shopify storefront data to competitive and market intelligence

The **Shopify Intelligence Pipeline** is an end-to-end data engineering system for collecting, validating, standardizing, enriching, and transforming fragmented Shopify storefront activity into historical, competitive, and market intelligence.

The initial vertical is **supplements**, where brands compete continuously on:

* product assortment
* pricing
* discounts
* promotions
* availability
* product launches
* customer perception
* brand positioning
* search visibility
* advertising activity
* competitive positioning

The business problem is not a lack of product data.

The problem is that **competitive signals are fragmented across storefronts and external intelligence sources, change continuously, and are rarely available as a unified historical dataset.**

A competitor can change a price, launch a product, remove an SKU, run a promotion, gain search visibility, increase advertising activity, or change its market positioning without creating a structured record that another business can easily analyze.

This pipeline creates that record.

> **The objective is not to scrape Shopify stores. The objective is to build a reliable intelligence system that converts fragmented e-commerce activity into historical, explainable, decision-ready data.**

---

# The Problem

A supplement brand monitoring competitors manually faces several problems:

```text
Competitor A ──┐
Competitor B ──┤
Competitor C ──┼──► Shopify storefronts
Competitor D ──┤
Competitor E ──┘
                │
                ▼
        Manual observation
                │
                ▼
        No reliable history
                │
                ▼
       Difficult to measure change
                │
                ▼
      Limited market context
```

A single storefront visit answers:

> **What is this competitor selling right now?**

It does not answer:

> What changed since yesterday?

> Which competitors are becoming more aggressive with pricing?

> Which products are repeatedly discounted?

> Which brands are expanding their assortment?

> Which products are becoming unavailable?

> Which products have similar competitive positioning?

> Which brands are generating stronger customer sentiment?

> Which competitors are gaining search, social, or advertising activity?

> How are prices positioned across markets?

> What market trends are emerging?

The pipeline is designed to answer these questions systematically.

---

# Business Objective

The system follows a simple principle:

```text
Business question
       ↓
Data signal
       ↓
Transformation
       ↓
Enrichment
       ↓
Intelligence product
       ↓
Decision
```

The intended users are:

### DTC and Supplement Brands

Need to understand:

* competitor pricing
* product launches
* promotions
* assortment changes
* availability
* customer sentiment
* competitor positioning
* market movement

### E-commerce and Merchandising Teams

Need to understand:

* which categories are expanding
* which products are being introduced
* how competitors position products
* where assortment gaps exist
* how prices compare
* where promotional pressure is increasing

### Competitive Intelligence Teams

Need to understand:

* what competitors changed
* how frequently they change it
* which competitors are becoming more aggressive
* how competitors compare
* where the market is moving

### Product and Market Researchers

Need structured evidence to identify:

* emerging products
* category activity
* pricing movements
* competitive patterns
* customer perception
* market trends

The pipeline therefore treats scraped data as an **input to intelligence**, not the final product.

---

# Architecture

The system has evolved from a Shopify crawler into a layered intelligence platform:

```text
                         SHOPIFY STOREFRONTS
                                  │
                                  ▼
                         ┌──────────────────┐
                         │    INGESTION     │
                         │                  │
                         │ Async HTTP/2     │
                         │ Catalog extraction│
                         │ Retries / fallback│
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │      BRONZE      │
                         │                  │
                         │ Raw observations │
                         │ Crawl metadata   │
                         │ Source metadata  │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │      SILVER      │
                         │                  │
                         │ Canonical products│
                         │ Variants         │
                         │ Pricing          │
                         │ Availability     │
                         │ Historical records│
                         └────────┬─────────┘
                                  │
                                  ▼
                    ┌─────────────────────────────┐
                    │         ENRICHMENT           │
                    │                             │
                    │ Internal-derived signals   │
                    │ External intelligence      │
                    │                             │
                    │ Reviews / Sentiment         │
                    │ Brand Reputation            │
                    │ SEO / Search                │
                    │ Social Engagement           │
                    │ Advertising                 │
                    │ Geographic Arbitrage        │
                    │ Competitor Benchmarks       │
                    │ Market Trends               │
                    └──────────────┬──────────────┘
                                   │
                                   ▼
                         ┌──────────────────┐
                         │       GOLD       │
                         │                  │
                         │ Pricing          │
                         │ Promotions       │
                         │ Product launches │
                         │ Inventory        │
                         │ Assortment       │
                         │ Competitors      │
                         │ Market intelligence│
                         └────────┬─────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             ▼             ▼
                Dashboard       API          Alerts
                    │             │             │
                    └─────────────┼─────────────┘
                                  ▼
                         BUSINESS DECISIONS
```

The platform is organized around six responsibilities:

```text
INGESTION
    ↓
BRONZE
    ↓
SILVER
    ↓
ENRICHMENT
    ↓
GOLD
    ↓
SERVING
```

> **Bronze preserves evidence. Silver creates trust. Enrichment adds context. Gold creates intelligence. Serving turns intelligence into action.**

---

# Current Implementation

The current pipeline monitors selected Shopify supplement storefronts, including:

* Transparent Labs
* Kaged
* GHOST Lifestyle
* Cellucor

The ingestion engine:

* crawls multiple storefronts concurrently
* uses asynchronous HTTP requests
* attempts Shopify Storefront GraphQL where configured
* falls back to public Shopify catalog endpoints
* extracts products and variants
* captures pricing and availability signals
* normalizes heterogeneous Shopify responses
* persists historical observations
* validates and deduplicates records
* produces analytical outputs

The pipeline has now progressed beyond ingestion into:

1. **Bronze source preservation**
2. **Silver canonicalization**
3. **Internal pricing enrichment**
4. **External intelligence enrichment**
5. **Integration-ready external API architecture**

---

# Bronze — Source Evidence

Bronze represents what the pipeline observed from Shopify storefronts.

Its responsibility is **preservation and traceability**, not business interpretation.

Typical metadata includes:

```text
store_url
crawl_timestamp
source_endpoint
crawl_id
raw_product_payload
raw_variant_payload
extraction_status
```

Bronze exists so downstream transformations can be:

* reproduced
* audited
* debugged
* reprocessed
* compared against source observations

The principle is:

> **Never destroy source evidence merely because a cleaner representation exists downstream.**

---

# Silver — Canonical E-commerce Dataset

The Silver layer is implemented through:

```text
silver_supplements_orchestrator.py
```

The architecture no longer moves directly from:

```text
scraped data
      ↓
analytics
```

Instead:

```text
Bronze
   ↓
Silver
   ↓
Enrichment
   ↓
Gold
```

The Silver orchestrator is responsible for:

* validation
* normalization
* type standardization
* record integrity
* deduplication
* canonical output

Conceptually:

```text
Bronze
  │
  ├── raw product records
  ├── raw variants
  ├── pricing observations
  └── crawl metadata
          │
          ▼
silver_supplements_orchestrator.py
          │
          ├── validation
          ├── normalization
          ├── type standardization
          ├── record integrity
          ├── deduplication
          └── canonical output
          │
          ▼
     Silver Dataset
```

Silver creates the **stable analytical contract** between ingestion and intelligence.

---

# Data Integrity

A major data-quality issue encountered during development was **duplicate records in downstream analytical outputs**.

The issue was identified and fixed during pipeline hardening.

This matters because duplicate observations can silently corrupt:

* product counts
* discount rankings
* inventory statistics
* competitor comparisons
* historical trends
* aggregate metrics

The architectural rule is:

> **A downstream analytical result is only as trustworthy as the uniqueness and lineage guarantees of the dataset underneath it.**

Silver therefore acts as the boundary for canonical record identity before enrichment and Gold transformations occur.

---

# Silver Data Model

## Store

```text
store_id
store_url
domain
crawl_timestamp
```

## Product

```text
product_id
store_id
title
handle
vendor
product_type
description
published_at
created_at
updated_at
```

## Variant

```text
variant_id
product_id
sku
title
price
compare_at_price
available
inventory_quantity
```

## Product Snapshot

```text
store_id
product_id
variant_id
crawl_timestamp
price
compare_at_price
availability
```

The snapshot concept is critical.

A current product record tells us:

> **What exists now?**

A historical snapshot tells us:

> **What existed at a particular point in time?**

A sequence of snapshots gives us:

> **What changed?**

That transition from:

```text
State
  ↓
History
  ↓
Change
  ↓
Intelligence
```

is the foundation of the platform.

---

# Enrichment Layer

The enrichment layer is now an implemented engineering boundary.

Its responsibility is to transform trusted Silver observations into **reusable intelligence vectors**.

The architecture separates internal product intelligence from external market context:

```text
                         SILVER
                           │
                ┌──────────┴──────────┐
                │                     │
                ▼                     ▼
       INTERNAL ENRICHMENT    EXTERNAL ENRICHMENT
                │                     │
                │                     ├── Reviews
                │                     ├── Reputation
                │                     ├── SEO
                │                     ├── Social
                │                     ├── Advertising
                │                     ├── Geography
                │                     ├── Competitors
                │                     └── Market Trends
                │                     │
                └──────────┬──────────┘
                           ▼
                    ENRICHED DATA
                           │
                           ▼
                          GOLD
```

---

# Internal Enrichment

The internal enrichment layer is grounded in real Shopify crawl data.

The primary pricing enrichment asset is:

```text
shopify_supplements_enrichment/
└── pricing_enrichment/
    └── price_metrics.json
```

The dataset provides the real product foundation used by the enrichment workflow:

```text
sku
product_title
store_url
current_price
```

The enrichment flow is therefore:

```text
Live Shopify Crawl
       ↓
Bronze
       ↓
Silver
       ↓
price_metrics.json
       ↓
Internal Enrichment Foundation
```

This establishes a key principle:

> **External intelligence is anchored to real products and prices observed from monitored Shopify storefronts.**

---

# External Intelligence Enrichment

The external enrichment architecture is implemented through:

```text
external_enricher.py
```

The enrichment orchestrator consumes the internal pricing foundation and coordinates eight intelligence domains.

```text
shopify_supplements_enrichment/
└── external_enrichment/
    ├── customer_reviews/
    ├── brand_reputation/
    ├── seo_search/
    ├── social_engagement/
    ├── ad_intelligence/
    ├── geographical_arbitrage/
    ├── competitor_similarity/
    └── market_trends/
```

The complete enrichment suite has been executed across:

> **2,059 base SKUs**

and successfully persisted the resulting intelligence assets.

---

# External API Integration Architecture

The external enrichment layer is not hard-coded around one provider.

The project includes:

```text
api_clients.py
```

which provides a modular gateway for external intelligence integrations.

The architecture is designed to support providers such as:

* Apify
* Bright Data
* DataForSEO
* Meta Ad Library
* other external intelligence providers

The client layer uses:

* environment-driven credential loading
* modular provider interfaces
* an `httpx` transport wrapper

Conceptually:

```text
                    external_enricher.py
                             │
                             ▼
                       api_clients.py
                             │
             ┌───────────────┼───────────────┐
             ▼               ▼               ▼
           Apify        Bright Data     DataForSEO
             │               │               │
             └───────────────┼───────────────┘
                             ▼
                    External Intelligence
```

This separation allows the enrichment orchestration layer to remain independent of individual external providers.

---

# External Enrichment Execution

During integration testing, a Python import-resolution issue was encountered when running the enrichment script directly.

The issue originated from sibling-module resolution and relative package imports.

The execution path was corrected by streamlining the import boundary to:

```python
from api_clients import ...
```

This allows:

```text
external_enricher.py
```

to execute cleanly from the repository root while retaining the modular API-client architecture.

The complete enrichment suite was then executed through PowerShell.

---

# External Intelligence Domains

## 1. Customer Sentiment & Reviews

Output:

```text
external_enrichment/customer_reviews/
```

The domain provides structured customer perception signals.

Potential intelligence dimensions include:

```text
rating
review_count
positive_sentiment
negative_sentiment
review_text
```

Business questions:

> Which products demonstrate stronger customer sentiment?

> Which brands show recurring negative feedback?

> Does customer perception align with pricing or product positioning?

---

# 2. Brand Reputation & Positioning

Output:

```text
external_enrichment/brand_reputation/
```

This domain provides brand-level competitive context.

Potential dimensions include:

```text
brand
reputation_score
brand_position
market_presence
```

The current implementation establishes the enrichment contract while the external API gateway provides the foundation for future live integrations.

Business questions:

> Which brands have stronger market reputation?

> How does brand positioning compare with product pricing?

---

# 3. SEO & Search Visibility

Output:

```text
external_enrichment/seo_search/
```

This domain models search visibility and product-level search activity.

Potential signals include:

```text
primary_keyword
search_volume
search_activity
search_visibility
```

The architecture is designed so modeled metrics can eventually be replaced by live search intelligence providers.

Business questions:

> Which products are gaining search attention?

> Which categories have stronger search visibility?

> Which competitors appear more visible in search?

---

# 4. Social Engagement & Viral Buzz

Output:

```text
external_enrichment/social_engagement/
```

Potential signals include:

```text
engagement
reach
social_activity
viral_coefficient
```

This creates a bridge between storefront activity and external attention.

```text
Storefront Activity
        +
Social Activity
        ↓
Competitive Attention
```

---

# 5. Advertising Intelligence

Output:

```text
external_enrichment/ad_intelligence/
```

Potential signals include:

```text
ad_count
advertising_activity
product_ad_presence
competitive_ad_pressure
```

The external client architecture provides a future path toward live advertising intelligence sources.

Business questions:

> Which competitors are increasing advertising activity?

> Which products are receiving paid promotional support?

> Is advertising pressure increasing around particular categories?

---

# 6. Geographical & Currency Arbitrage

Output:

```text
external_enrichment/geographical_arbitrage/
```

This domain establishes a framework for comparing product economics across geographic markets.

Potential signals include:

```text
domestic_price
uk_price
eu_price
regional_price_spread
currency_effect
arbitrage_signal
```

Business questions:

> How does a product's price vary across markets?

> Which competitors show larger regional pricing spreads?

---

# 7. Cross-Brand Competitor Benchmarks

Output:

```text
external_enrichment/competitor_similarity/
```

This domain moves analysis from individual products toward competitive sets.

Potential signals include:

```text
product_similarity
competitor_similarity_score
category_overlap
price_similarity
assortment_overlap
```

The analytical progression becomes:

```text
Product
   ↓
Similar Products
   ↓
Competitive Set
   ↓
Competitor Benchmark
```

This is critical for future competitive positioning analysis.

---

# 8. Market Trend Velocities

Output:

```text
external_enrichment/market_trends/
```

This is the highest-level external intelligence domain in the current enrichment framework.

Potential dimensions include:

```text
category_trend
market_activity
pricing_trend
demand_proxy
competitive_pressure
trend_velocity
```

The goal is to connect product-level observations with broader market movement.

---

# Enrichment Provenance

The enrichment layer follows a strict provenance principle.

Not every metric in the enrichment layer has the same origin.

The architecture distinguishes:

```text
INTERNAL OBSERVATION
        ↓
Derived from actual Shopify data

EXTERNAL SOURCE
        ↓
Retrieved from a production external provider

SIMULATED EXTERNAL
        ↓
Fallback intelligence generated when live external
provider data is unavailable
```

The current verified execution used the **fallback simulation engine** to successfully generate and persist the eight intelligence domains across all 2,059 base SKUs.

This distinction is intentional.

The pipeline therefore has two capabilities:

```text
                    EXTERNAL ENRICHMENT
                            │
             ┌──────────────┴──────────────┐
             ▼                             ▼
       LIVE PROVIDERS                 FALLBACK ENGINE
             │                             │
             └──────────────┬──────────────┘
                            ▼
                  STANDARDIZED ENRICHMENT
                            │
                            ▼
                           GOLD
```

This allows downstream analytical development to continue while individual external data integrations are progressively productionized.

> **The fallback engine validates the enrichment architecture; live providers will validate the external data acquisition layer.**

---

# Enrichment Output

The verified run successfully processed:

```text
Base SKUs: 2,059
```

Across eight intelligence domains:

```text
1. Customer Sentiment & Reviews
2. Brand Reputation & Positioning
3. SEO & Search Visibility
4. Social Engagement & Viral Buzz
5. Advertising Intelligence
6. Geographical & Currency Arbitrage
7. Cross-Brand Competitor Benchmarks
8. Market Trend Velocities
```

The resulting JSON assets are persisted under:

```text
shopify_supplements_enrichment/
└── external_enrichment/
    ├── customer_reviews/
    ├── brand_reputation/
    ├── seo_search/
    ├── social_engagement/
    ├── ad_intelligence/
    ├── geographical_arbitrage/
    ├── competitor_similarity/
    └── market_trends/
```

These datasets are now ready for downstream aggregation, validation, Gold modeling, visualization, and eventual serving.

---

# Gold — Decision-Ready Intelligence

Gold is not another copy of Silver.

Silver answers:

> **What did we observe?**

Enrichment answers:

> **What additional context surrounds the observation?**

Gold answers:

> **What does the combined evidence mean for a business decision?**

The Gold layer is therefore organized around business questions rather than database entities.

```text
gold/
├── competitive_pricing/
├── promotion_intelligence/
├── product_launches/
├── inventory_intelligence/
├── assortment_intelligence/
├── competitor_intelligence/
└── market_intelligence/
```

---

# Gold Product 1 — Competitive Pricing Intelligence

```text
competitive_pricing/
├── price_history.parquet
├── price_changes.parquet
├── price_position.parquet
└── pricing_summary.parquet
```

Potential outputs:

```text
current_price
previous_price
price_change
discount_percentage
competitor_median_price
competitor_min_price
competitor_max_price
relative_price_position
regional_price_spread
```

Business question:

> **Are competitors becoming more aggressive on price?**

---

# Gold Product 2 — Promotion Intelligence

```text
promotion_intelligence/
├── active_promotions.parquet
├── promotion_history.parquet
├── discount_benchmarks.parquet
└── promotion_frequency.parquet
```

Business questions:

> Who discounts most aggressively?

> Which products are repeatedly promoted?

> Is promotional pressure increasing?

---

# Gold Product 3 — Product Launch Intelligence

```text
product_launches/
├── new_products.parquet
├── discontinued_products.parquet
└── category_expansion.parquet
```

Business question:

> **What are competitors launching?**

---

# Gold Product 4 — Assortment Intelligence

```text
assortment_intelligence/
├── store_assortment.parquet
├── category_coverage.parquet
├── product_overlap.parquet
└── assortment_changes.parquet
```

Business questions:

> Which categories does each competitor cover?

> Where are the assortment gaps?

> Which competitors are expanding into new categories?

---

# Gold Product 5 — Inventory Intelligence

The system does not treat storefront availability as exact inventory.

Instead, it produces defensible availability signals.

```text
inventory_intelligence/
├── availability_history.parquet
├── stockout_events.parquet
└── availability_summary.parquet
```

Business questions:

> Which products repeatedly become unavailable?

> Which competitors have persistent availability problems?

---

# Gold Product 6 — Competitor Intelligence

This layer combines storefront events with enrichment vectors.

```text
competitor_intelligence/
├── competitor_events.parquet
├── competitor_activity.parquet
└── competitor_scorecards.parquet
```

A future competitor scorecard can combine:

```text
Product launches
Price changes
Promotional activity
Availability changes
Customer sentiment
Brand reputation
Search visibility
Social engagement
Advertising activity
Geographic pricing
Competitor similarity
Market trends
```

This transforms multiple disconnected signals into a single competitor-level intelligence view.

---

# Gold Product 7 — Market Intelligence

```text
market_intelligence/
├── category_trends.parquet
├── pricing_trends.parquet
├── promotion_trends.parquet
├── product_launch_trends.parquet
└── competitive_activity.parquet
```

The analytical hierarchy becomes:

```text
Variant
   ↓
Product
   ↓
Brand
   ↓
Category
   ↓
Competitive Set
   ↓
Market
```

With enrichment:

```text
Product
   +
Price
   +
Customer perception
   +
Search
   +
Social
   +
Advertising
   +
Geography
   +
Competition
   +
Market trends
```

This is where the pipeline begins to move from **storefront monitoring** toward **market intelligence**.

---

# From Data Pipeline to Intelligence Products

The Parquet datasets are not the final customer product.

They are the **data products underneath customer-facing products**.

```text
                         GOLD
                          │
             ┌────────────┼────────────┐
             ▼            ▼            ▼
         Dashboard       API         Alerts
             │            │            │
             ▼            ▼            ▼
      Human analysis  Integration    Action
```

Potential products include:

## Competitive Intelligence Dashboard

```text
COMPETITOR ACTIVITY — WEEKLY

GHOST
  4 new products
  7 price changes
  12 active promotions
  ↑ search activity
  ↑ social engagement

KAGED
  8 new products
  3 price increases
  2 stockout events
  ↑ advertising activity

TRANSPARENT LABS
  5 new products
  6 price changes
  strong customer sentiment
```

## Competitive Price Alerts

```text
PRICE CHANGE DETECTED

Competitor: GHOST
Product: Whey Protein

Previous: $59.99
Current:  $49.99
Change:   -16.7%
```

## Product Launch Alerts

```text
NEW PRODUCT DETECTED

Competitor: KAGED
Category: Creatine
```

## Weekly Market Intelligence

```text
SUPPLEMENT MARKET
WEEKLY INTELLIGENCE

Pricing
Average monitored price ↓ 3.2%

Promotions
Promotional activity ↑ 14%

New Products
23 new products detected

Availability
11 products experienced stockouts

Search
Search activity ↑

Advertising
Competitive ad activity ↑

Most active competitor
Brand X
```

---

# Current Repository Structure

The repository is evolving toward explicit separation between ingestion, transformation, enrichment, and serving.

```text
.
├── Shopify-Supplements/
│   ├── pipeline.py
│   ├── engine.py
│   ├── graphql_client.py
│   ├── normalizer.py
│   ├── db_manager.py
│   ├── analytics.py
│   ├── config.py
│   └── silver_supplements_orchestrator.py
│
├── shopify_supplements_enrichment/
│   ├── pricing_enrichment/
│   │   └── price_metrics.json
│   │
│   ├── external_enrichment/
│   │   ├── customer_reviews/
│   │   ├── brand_reputation/
│   │   ├── seo_search/
│   │   ├── social_engagement/
│   │   ├── ad_intelligence/
│   │   ├── geographical_arbitrage/
│   │   ├── competitor_similarity/
│   │   └── market_trends/
│   │
│   ├── external_enricher.py
│   └── api_clients.py
│
├── shopify/
│   └── pipeline.py
│
├── tests/
│
├── shopify_intelligence.db
├── shopify_supplement_intelligence.json
└── README.md
```

---

# Pipeline Responsibilities

| Component                            | Responsibility                               |
| ------------------------------------ | -------------------------------------------- |
| `engine.py`                          | Async storefront collection                  |
| `graphql_client.py`                  | Shopify Storefront GraphQL access            |
| `normalizer.py`                      | Canonical product and variant transformation |
| `db_manager.py`                      | Persistence and database management          |
| `pipeline.py`                        | End-to-end ingestion orchestration           |
| `silver_supplements_orchestrator.py` | Bronze → Silver transformation               |
| `external_enricher.py`               | Coordinates external intelligence enrichment |
| `api_clients.py`                     | External provider integration gateway        |
| `analytics.py`                       | Analytical reporting                         |
| `tests/`                             | Automated validation                         |

The architectural direction is:

```text
Ingestion
    ↓
Transformation
    ↓
Enrichment
    ↓
Gold Modeling
    ↓
Serving
```

Business logic should remain outside the crawler wherever possible.

---

# Data Quality & Observability

Data quality is a core product requirement because incorrect competitive intelligence can lead to incorrect business decisions.

The pipeline prioritizes:

### Uniqueness

Prevent duplicate observations from inflating metrics.

### Completeness

Validate required product, variant, source, and timestamp fields.

### Consistency

Map heterogeneous storefront responses into a stable canonical model.

### Historical Integrity

Preserve previous observations for longitudinal analysis.

### Lineage

Maintain traceability from intelligence back to source observations.

### Provenance

Distinguish:

```text
Observed
Derived
External
Simulated
```

### Observability

Pipeline runs should expose:

```text
run_id
crawl_timestamp
source
records_extracted
records_valid
records_rejected
processing_duration
errors
```

Enrichment execution should additionally track:

```text
enrichment_domain
base_sku_count
records_enriched
provider
fallback_used
execution_status
```

---

# What Has Been Completed

## Ingestion

* [x] Async Shopify storefront crawling
* [x] Concurrent multi-store collection
* [x] Shopify Storefront GraphQL support
* [x] Public catalog endpoint fallback
* [x] Product and variant extraction

## Normalization

* [x] Canonical product records
* [x] Variant-level records
* [x] Pricing fields
* [x] Availability signals
* [x] Crawl timestamps

## Data Integrity

* [x] Duplicate-record issue identified
* [x] Duplicate-record issue fixed
* [x] Historical persistence maintained
* [x] Data quality controls established

## Silver

* [x] Silver architecture established
* [x] `silver_supplements_orchestrator.py` implemented
* [x] Bronze → Silver transformation boundary established
* [x] Canonical analytical dataset introduced

## Internal Enrichment

* [x] Pricing enrichment implemented
* [x] Real Shopify pricing foundation established
* [x] `price_metrics.json` generated
* [x] SKU-level enrichment foundation established

## External Enrichment

* [x] `external_enricher.py` implemented
* [x] `api_clients.py` modular gateway established
* [x] Environment-driven credential architecture established
* [x] HTTP transport wrapper established
* [x] External provider integration architecture established
* [x] Import/path execution issue resolved
* [x] Full enrichment suite executed
* [x] 2,059 base SKUs processed
* [x] Customer sentiment & reviews generated
* [x] Brand reputation & positioning generated
* [x] SEO & search visibility generated
* [x] Social engagement & viral buzz generated
* [x] Advertising intelligence generated
* [x] Geographical & currency arbitrage generated
* [x] Cross-brand competitor benchmarks generated
* [x] Market trend velocities generated
* [x] JSON intelligence assets persisted

## External Data Acquisition

* [ ] Connect production provider credentials
* [ ] Replace fallback simulation with live external observations
* [ ] Add provider-level lineage
* [ ] Add source freshness monitoring
* [ ] Add enrichment confidence scoring

---

# Current Engineering Position

The project is no longer:

```text
Shopify scraper
```

It is now:

```text
Shopify Ingestion
        ↓
     Bronze
        ↓
     Silver
        ↓
Internal Enrichment
        +
External Intelligence
        ↓
      Gold
        ↓
Intelligence Products
        ↓
Business Decisions
```

The critical architectural shift is that **the pipeline now has an intelligence context layer surrounding its Shopify observations**.

The next priority is not simply collecting more storefront records.

It is:

> **Turning the 2,059-SKU enriched dataset into validated Gold data products that answer specific competitive and market questions.**

---

# Roadmap

## Phase 1 — Ingestion

* [x] Multi-store asynchronous collection
* [x] Shopify endpoint handling
* [x] Product and variant extraction
* [x] Historical persistence

## Phase 2 — Silver

* [x] Canonical data model
* [x] Silver orchestration
* [x] Deduplication
* [x] Data integrity controls
* [x] Historical snapshots

## Phase 3 — Enrichment

* [x] Internal pricing enrichment
* [x] External enrichment architecture
* [x] Customer sentiment & reviews
* [x] Brand reputation
* [x] SEO/search visibility
* [x] Social engagement
* [x] Advertising intelligence
* [x] Geographical arbitrage
* [x] Competitor benchmarks
* [x] Market trends
* [x] External API client architecture
* [x] Fallback enrichment execution
* [x] 2,059-SKU enrichment run

## Phase 4 — Gold

* [ ] Competitive Pricing Intelligence
* [ ] Promotion Intelligence
* [ ] Product Launch Intelligence
* [ ] Inventory Intelligence
* [ ] Assortment Intelligence
* [ ] Competitor Intelligence
* [ ] Market Intelligence
* [ ] Cross-domain competitor scoring

## Phase 5 — Serving

* [ ] Gold Parquet data products
* [ ] BI dashboard
* [ ] Competitive alerts
* [ ] Intelligence API
* [ ] Scheduled reports
* [ ] Automated competitor scorecards

## Phase 6 — Production External Intelligence

* [ ] Production Apify integrations
* [ ] Production Bright Data integrations
* [ ] Production DataForSEO integrations
* [ ] Production Meta Ad Library integration
* [ ] Live review intelligence
* [ ] Live search intelligence
* [ ] Live social intelligence
* [ ] Live advertising intelligence
* [ ] Live geographic pricing
* [ ] External source freshness tracking
* [ ] Provider reliability scoring

## Phase 7 — Expansion

* [ ] Additional Shopify verticals
* [ ] Additional e-commerce sources
* [ ] Cross-marketplace intelligence
* [ ] Cross-platform product identity
* [ ] Broader e-commerce intelligence platform

---

# Design Principles

## 1. Business Question Before Source

A source should not be added simply because it can be scraped or queried.

Ask:

> **Who needs this data, what decision does it support, and why would they pay for it?**

## 2. Raw Data Is Evidence

Bronze preserves what happened.

## 3. Silver Is the Analytical Contract

Silver provides the stable, validated, canonical representation downstream consumers can trust.

## 4. Enrichment Creates Context

Enrichment adds reusable intelligence vectors around canonical observations.

```text
Observation
     ↓
Derived Signal
     ↓
External Context
     ↓
Intelligence Vector
```

## 5. Provenance Is Non-Negotiable

A simulated metric must never be presented as a live external observation.

The system must preserve the distinction between:

```text
Observed
Derived
External
Simulated
```

## 6. Gold Represents Decisions

Gold should answer:

```text
What changed?

Who changed it?

How significant was the change?

How does it compare with competitors?

What external signals surround the change?

What market pattern is emerging?

What should the business investigate or act on?
```

## 7. Historical Data Is a Product

```text
Snapshot
   ↓
History
   ↓
Change
   ↓
Trend
   ↓
Context
   ↓
Intelligence
```

## 8. Reliability Before Scale

The goal is not to collect millions of records simply to demonstrate scraping scale.

The goal is to produce:

> **Trustworthy, explainable signals that survive repeated pipeline runs and support real decisions.**

## 9. Separate Acquisition From Intelligence

The crawler collects evidence.

Silver standardizes it.

Enrichment adds context.

Gold creates decisions.

Serving delivers those decisions.

---

# Long-Term Vision

The long-term objective is to evolve the project from a Shopify-specific pipeline into an **E-commerce Intelligence Platform**.

```text
                  E-COMMERCE SOURCES
                         │
         ┌───────────────┼────────────────┐
         │               │                │
      Shopify         Amazon         Marketplaces
         │               │                │
         └───────────────┼────────────────┘
                         ▼
                      BRONZE
                   Source Evidence
                         │
                         ▼
                      SILVER
                Canonical Data Model
                         │
                         ▼
                    ENRICHMENT
              Signals + Context + Events
                         │
                         ▼
                       GOLD
                 Decision-Ready Data
                         │
         ┌───────────────┼────────────────┐
         ▼               ▼                ▼
      Pricing         Product          Market
   Intelligence     Intelligence     Intelligence
         │               │                │
         └───────────────┼────────────────┘
                         ▼
                  DATA PRODUCTS
                         │
         ┌───────────────┼────────────────┐
         ▼               ▼                ▼
     Dashboards         APIs            Alerts
                         │
                         ▼
                 BUSINESS DECISIONS
```

The strategic objective is not to build the largest Shopify scraper.

It is to build a **reliable intelligence system that converts fragmented e-commerce activity into historical, explainable, decision-ready data.**

The crawler collects the evidence.

**Bronze preserves it.**

**Silver makes it trustworthy.**

**Enrichment adds context.**

**Gold makes it useful.**

**Data products make it valuable.**
