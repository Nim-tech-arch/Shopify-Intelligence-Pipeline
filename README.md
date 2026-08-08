# Shopify Intelligence Pipeline

## Turning fragmented Shopify storefront activity into competitive intelligence

The **Shopify Intelligence Pipeline** is an end-to-end data engineering system for collecting, validating, standardizing, and transforming Shopify storefront data into decision-ready e-commerce intelligence.

The initial vertical is **supplements**, where brands compete continuously on:

* product assortment
* pricing
* discounts
* promotions
* availability
* product launches
* merchandising strategy

The business problem is not a lack of product data.

The problem is that **competitive signals are fragmented across independent storefronts and change continuously**.

A competitor can change a price, launch a product, remove an SKU, or run a promotion without creating a structured record that another business can easily analyze.

This pipeline creates that record.

> **The objective is not to scrape Shopify stores. The objective is to build a reliable historical intelligence layer that explains what competitors are doing and how the market is changing.**

---

# The Problem

A supplement brand monitoring competitors manually faces several problems:

```text
Competitor A ──┐
Competitor B ──┤
Competitor C ──┼──► Fragmented storefronts
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
```

A single storefront visit answers:

> **What is this competitor selling right now?**

It does not answer:

> What changed since yesterday?

> Which competitors are becoming more aggressive with pricing?

> Which products are repeatedly discounted?

> Which brands are expanding their assortment?

> Which products are becoming unavailable?

> Which categories are becoming more competitive?

The pipeline is designed to answer those questions systematically.

---

# Business Objective

The system is built around a simple principle:

> **Business question → data signal → transformation → intelligence product → decision**

The intended users are:

### DTC and supplement brands

Need to understand:

* competitor pricing
* product launches
* promotions
* assortment changes
* availability signals

### E-commerce and merchandising teams

Need to understand:

* which categories are expanding
* which products are being introduced
* how competitors position products
* where assortment gaps exist

### Competitive intelligence teams

Need to understand:

* what competitors changed
* how frequently they change it
* which competitors are becoming more aggressive
* where the market is moving

### Product and market researchers

Need structured historical evidence to identify:

* emerging products
* category activity
* pricing movements
* competitive patterns

The pipeline therefore treats scraped data as an **input to intelligence**, not the final product.

---

# Architecture

The system now implements the first three major stages of the data platform:

```text
                 SHOPIFY STOREFRONTS
                         │
                         ▼
              ┌────────────────────┐
              │     INGESTION      │
              │                    │
              │ Async HTTP/2       │
              │ Catalog extraction │
              │ Retries / fallback │
              └─────────┬──────────┘
                        │
                        ▼
              ┌────────────────────┐
              │      BRONZE        │
              │                    │
              │ Raw observations   │
              │ Crawl metadata     │
              │ Source metadata    │
              └─────────┬──────────┘
                        │
                        ▼
              ┌────────────────────┐
              │      SILVER        │
              │                    │
              │ Canonical products │
              │ Variants           │
              │ Pricing            │
              │ Availability       │
              │ Store metadata     │
              │ Historical records │
              └─────────┬──────────┘
                        │
                        ▼
              ┌────────────────────┐
              │    ENRICHMENT      │
              │                    │
              │ Pricing signals    │
              │ Product events     │
              │ Promotions         │
              │ Taxonomy           │
              │ Competition        │
              └─────────┬──────────┘
                        │
                        ▼
              ┌────────────────────┐
              │       GOLD         │
              │                    │
              │ Pricing            │
              │ Promotions         │
              │ Product launches   │
              │ Inventory          │
              │ Assortment         │
              │ Market intelligence│
              └─────────┬──────────┘
                        │
             ┌──────────┼──────────┐
             ▼          ▼          ▼
          Dashboard    API       Alerts
             │          │          │
             └──────────┼──────────┘
                        ▼
                BUSINESS DECISIONS
```

**Bronze and Silver are implemented. Enrichment and Gold are the next major engineering boundary.**

---

# Current Implementation

The current pipeline monitors selected Shopify supplement storefronts, including brands such as:

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

The pipeline has now progressed beyond ingestion into a dedicated **Silver data layer**.

---

# Data Layers

## Bronze — Source Evidence

Bronze represents what the pipeline observed from the source.

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

Bronze exists so that downstream transformations can be:

* reproduced
* audited
* debugged
* reprocessed
* compared against source observations

The principle is:

> **Never destroy source evidence merely because a cleaner representation exists downstream.**

---

# Silver — Canonical E-commerce Dataset

The Silver layer is now implemented through:

```text
silver_supplements_orchestrator.py
```

This is an important architectural transition.

The pipeline no longer moves directly from:

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
Analytics / Enrichment / Gold
```

The Silver orchestrator is responsible for taking collected storefront observations and producing a consistent analytical representation suitable for downstream processing.

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

## Why Silver matters

Raw Shopify responses are optimized for storefront delivery.

They are not optimized for:

* historical comparison
* cross-store analysis
* data quality checks
* analytics
* event detection
* competitive benchmarking

Silver creates the **stable analytical contract** between ingestion and intelligence.

---

# Data Integrity

A major data-quality issue encountered during development was **duplicate records in downstream analytical outputs**.

The issue was fixed as part of the pipeline hardening work.

This matters because duplicate observations can silently corrupt:

* product counts
* discount rankings
* inventory statistics
* competitor comparisons
* historical trends
* aggregate metrics

The pipeline therefore treats data integrity as a first-class engineering concern rather than an afterthought.

The architectural rule is:

> **A downstream analytical result is only as trustworthy as the uniqueness and lineage guarantees of the dataset underneath it.**

Silver is therefore the appropriate boundary for enforcing canonical record identity before enrichment and Gold transformations occur.

---

# Silver Data Model

The Silver layer is designed around several core entities.

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

That transition from **state → history → change** is the foundation of the intelligence layer.

---

# Enrichment Layer

The next major transformation boundary is enrichment.

Silver should contain **canonical observations**.

It should not become a dumping ground for every possible business metric.

Enrichment should derive reusable signals from those observations.

Potential enrichment domains include:

## Pricing

```text
discount_amount
discount_percentage
previous_price
price_change
price_change_percentage
7d_price_change
30d_price_change
minimum_observed_price
maximum_observed_price
median_observed_price
price_volatility
```

## Availability

```text
availability_status
availability_change
availability_rate
stockout_frequency
consecutive_unavailable_snapshots
```

Availability should remain an **observed signal** unless the source provides reliable inventory quantities.

---

## Product Lifecycle

Repeated snapshots enable event detection:

```text
NEW_PRODUCT
PRICE_CHANGE
PRICE_DROP
PRICE_INCREASE
DISCOUNT_STARTED
DISCOUNT_ENDED
PRODUCT_REMOVED
AVAILABILITY_CHANGED
```

This converts snapshots into a chronological stream of competitive events.

---

## Promotion

Potential derived signals:

```text
promotion_status
discount_percentage
promotion_frequency
promotion_duration
days_since_last_promotion
```

This enables questions such as:

> Which competitors rely most heavily on promotions?

---

## Product Taxonomy

Different Shopify stores may describe similar products differently.

For example:

```text
Whey Protein Isolate
100% Whey
Grass-Fed Whey
Whey Isolate Protein
```

The enrichment layer can progressively map these into a canonical taxonomy:

```text
Protein
├── Whey
├── Casein
├── Plant
└── Mass Gainer

Performance
├── Creatine
├── Pre-Workout
├── BCAA
└── Electrolytes
```

This enables meaningful cross-store comparisons.

---

# Gold — Decision-Ready Intelligence

Gold should not be another copy of Silver.

Silver answers:

> **What did we observe?**

Gold should answer:

> **What does the observation mean for a business decision?**

The Gold layer will therefore be organized around **business questions rather than database entities**.

Proposed structure:

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

### Business problem

Competitors can change prices without providing a structured historical record.

### Gold dataset

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
```

This supports:

> **Are competitors becoming more aggressive on price?**

---

# Gold Product 2 — Promotion Intelligence

### Business problem

Discounting is often visible at the storefront level but difficult to analyze across competitors and time.

### Gold dataset

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

Repeated snapshots enable detection of products entering and leaving competitor catalogs.

```text
product_launches/
├── new_products.parquet
├── discontinued_products.parquet
└── category_expansion.parquet
```

Business question:

> **What are competitors launching?**

This could eventually become a weekly competitive intelligence report or automated alert product.

---

# Gold Product 4 — Assortment Intelligence

Compare monitored stores across normalized product categories.

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

The objective is not to pretend that storefront availability equals exact inventory.

Instead, build defensible availability signals.

```text
inventory_intelligence/
├── availability_history.parquet
├── stockout_events.parquet
└── availability_summary.parquet
```

Business questions:

> Which products repeatedly become unavailable?

> Which competitors have persistent availability problems?

> Are certain categories experiencing increasing stockouts?

---

# Gold Product 6 — Competitor Activity Intelligence

This is the layer that combines individual events into a competitor-level view.

```text
competitor_intelligence/
├── competitor_events.parquet
├── competitor_activity.parquet
└── competitor_scorecards.parquet
```

Example events:

```text
+ 5 new products
↓ 12 prices
% 8 active promotions
× 3 products removed
! 7 availability changes
```

A brand could therefore receive a weekly competitor scorecard rather than manually reviewing four websites.

---

# Gold Product 7 — Market Intelligence

This is the highest aggregation layer.

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

This enables the system to move from product-level scraping toward **market-level intelligence**.

---

# From Data Pipeline to End-to-End Products

The Parquet datasets are not the final customer product.

They are the **data products underneath the customer-facing products**.

The architecture can ultimately support:

```text
                     GOLD DATA
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
      Dashboard         API           Alerts
          │              │              │
          ▼              ▼              ▼
   Human analysis   System integration  Action
```

## 1. Competitive Intelligence Dashboard

A brand could see:

```text
COMPETITOR ACTIVITY — WEEKLY

GHOST
  4 new products
  7 price changes
  12 active promotions

KAGED
  8 new products
  3 price increases
  2 stockout events

TRANSPARENT LABS
  5 new products
  6 price changes
```

---

## 2. Competitive Price Alerts

Example:

```text
PRICE CHANGE DETECTED

Competitor: GHOST
Product: Whey Protein

Previous: $59.99
Current:  $49.99
Change:   -16.7%

Detected: 2026-08-08
```

---

## 3. Product Launch Alerts

```text
NEW PRODUCT DETECTED

Competitor: Kaged
Category: Creatine

Detected: 2026-08-08
```

---

## 4. Weekly Market Intelligence Report

The pipeline could eventually generate:

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

Most active competitor
Brand X
```

---

# Current Repository Structure

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
├── shopify/
│   └── pipeline.py
│
├── tests/
│   ├── test_pipeline.py
│   ├── test_engine.py
│   ├── test_graphql_client.py
│   ├── test_normalizer.py
│   ├── test_db_manager.py
│   ├── test_analytics.py
│   └── test_config.py
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
| `graphql_client.py`                  | Storefront GraphQL access                    |
| `normalizer.py`                      | Canonical product and variant transformation |
| `db_manager.py`                      | Persistence and database management          |
| `pipeline.py`                        | End-to-end ingestion orchestration           |
| `silver_supplements_orchestrator.py` | Bronze → Silver transformation               |
| `analytics.py`                       | Current analytical reporting                 |
| `config.py`                          | Source and runtime configuration             |
| `tests/`                             | Automated validation                         |

The architectural direction is to progressively separate:

```text
Ingestion
Transformation
Enrichment
Gold modeling
Serving
```

rather than allowing business logic to accumulate inside the crawler.

---

# Data Quality Strategy

Data quality is a core part of the product because incorrect competitive intelligence can lead to incorrect business decisions.

The pipeline therefore prioritizes:

### Uniqueness

Prevent duplicate observations from inflating metrics.

### Completeness

Required product, variant, source, and timestamp fields should be validated.

### Consistency

Different storefront responses should map to a stable canonical model.

### Historical integrity

Previous observations should remain available for longitudinal analysis.

### Lineage

Every analytical record should be traceable back to its source and crawl.

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

---

# What Has Been Completed

The project has now progressed through several important engineering milestones.

### Ingestion

* [x] Async Shopify storefront crawling
* [x] Concurrent multi-store collection
* [x] Storefront GraphQL support
* [x] Public catalog endpoint fallback
* [x] Product and variant extraction

### Normalization

* [x] Canonical product records
* [x] Variant-level records
* [x] Pricing fields
* [x] Availability signals
* [x] Crawl timestamps

### Data Integrity

* [x] Duplicate-record issue identified
* [x] Duplicate-record issue fixed
* [x] Historical persistence maintained
* [x] Data quality treated as a pipeline concern

### Silver Layer

* [x] Silver architecture established
* [x] `silver_supplements_orchestrator.py` implemented
* [x] Bronze → Silver transformation boundary established
* [x] Canonical analytical dataset introduced

### Analytics

* [x] Discount analysis
* [x] Inventory/availability analysis
* [x] Store-level analytical reporting

---

# Current Engineering Position

The project is no longer simply:

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
Enrichment
        ↓
Gold
        ↓
Intelligence Products
```

The next architectural priority is **not more scraping**.

It is extracting more value from the data already being collected.

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

* [ ] Pricing enrichment
* [ ] Price-change detection
* [ ] Promotion classification
* [ ] Product lifecycle events
* [ ] Availability events
* [ ] Product taxonomy
* [ ] Cross-store product identity
* [ ] Competitive price positioning

## Phase 4 — Gold

* [ ] Competitive Pricing Intelligence
* [ ] Promotion Intelligence
* [ ] Product Launch Intelligence
* [ ] Inventory Intelligence
* [ ] Assortment Intelligence
* [ ] Competitor Intelligence
* [ ] Market Intelligence

## Phase 5 — Serving

* [ ] Gold Parquet data products
* [ ] BI dashboard
* [ ] Competitive alerts
* [ ] Intelligence API
* [ ] Scheduled reports

## Phase 6 — Expansion

* [ ] Additional Shopify verticals
* [ ] Additional e-commerce sources
* [ ] Cross-marketplace intelligence
* [ ] Broader e-commerce intelligence platform

---

# Design Principles

## 1. Business question before source

A source should not be added simply because it can be scraped.

Ask:

> **Who needs this data, what decision does it support, and why would they pay for it?**

---

## 2. Raw data is evidence

Bronze preserves what happened.

It should remain close to the source.

---

## 3. Silver is the analytical contract

Silver provides the stable, validated, canonical representation that downstream consumers can trust.

---

## 4. Enrichment creates reusable signals

Enrichment converts observations into measurable attributes and events.

```text
Observation
    ↓
Derived Signal
```

Examples:

```text
price + previous price
        ↓
price_change

price + compare_at_price
        ↓
discount_percentage

snapshot A + snapshot B
        ↓
product_event
```

---

## 5. Gold represents decisions

Gold should answer:

```text
What changed?

Who changed it?

How significant was the change?

How does it compare with competitors?

What market pattern is emerging?
```

---

## 6. Historical data is a product

The value of the system increases as historical observations accumulate.

```text
Snapshot
   ↓
History
   ↓
Change
   ↓
Trend
   ↓
Intelligence
```

---

## 7. Reliability before scale

The goal is not to collect millions of records simply to demonstrate scraping scale.

The goal is to produce **trustworthy signals that survive repeated pipeline runs and support real decisions**.

---

# Long-Term Vision

The long-term objective is to evolve the project from a Shopify-specific pipeline into an **E-commerce Intelligence Platform**.

```text
                 E-COMMERCE SOURCES
                         │
        ┌────────────────┼────────────────┐
        │                │                │
     Shopify          Amazon          Marketplaces
        │                │                │
        └────────────────┼────────────────┘
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
             Signals + Events + Taxonomy
                         │
                         ▼
                     GOLD
               Decision-Ready Data
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
     Pricing         Product          Market
  Intelligence     Intelligence     Intelligence
        │                │                │
        └────────────────┼────────────────┘
                         ▼
              ┌────────────────────┐
              │  DATA PRODUCTS     │
              │                    │
              │ Dashboards         │
              │ APIs               │
              │ Alerts             │
              │ Reports            │
              └─────────┬──────────┘
                        ▼
                BUSINESS DECISIONS
```

The strategic objective is therefore not to build the largest Shopify scraper.

It is to build a **reliable intelligence system that converts fragmented e-commerce activity into historical, explainable, decision-ready data.**

The crawler collects the evidence.

**Bronze preserves it.**

**Silver makes it trustworthy.**

**Enrichment makes it meaningful.**

**Gold makes it useful.**

**Data products make it valuable.**
