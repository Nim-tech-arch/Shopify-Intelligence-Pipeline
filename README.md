# Shopify Intelligence Pipeline

## From Shopify storefront data to product, pricing, and market intelligence

The **Shopify Intelligence Pipeline** is an extensible data engineering pipeline for transforming fragmented Shopify storefront data into structured, analytics-ready intelligence.

The project is built around a simple principle:

> **Do not scrape data without a business question. Collect the signals required to support a decision.**

Instead of treating Shopify stores as isolated websites to scrape, the pipeline treats them as **commercial data sources** that expose signals about products, pricing, inventory, merchandising, discounts, and emerging market activity.

The current implementation focuses on **Shopify supplement stores** and establishes the foundation for expanding into additional verticals such as pet products, fashion, beauty, home goods, and other e-commerce categories.

---

## Why this data matters

E-commerce businesses do not pay for raw product records.

They pay for intelligence that helps answer questions such as:

* What products are competitors selling?
* How are competitors pricing similar products?
* Which products are being discounted?
* Which products appear to be gaining or losing availability?
* What new products are entering a niche?
* How does a store's assortment compare with competitors?
* Which categories or products deserve closer investigation?
* Where are pricing and merchandising strategies changing?

The pipeline therefore follows an **ELT-oriented architecture**:

```text
Shopify Storefronts
       │
       ▼
┌──────────────────┐
│   BRONZE LAYER   │
│                  │
│ Raw storefront   │
│ catalog data     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   SILVER LAYER   │
│                  │
│ Normalized       │
│ products         │
│ variants         │
│ prices           │
│ inventory        │
│ brands           │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│    GOLD LAYER    │
│                  │
│ Pricing          │
│ Product          │
│ Inventory        │
│ Promotion        │
│ Market           │
│ Intelligence     │
└────────┬─────────┘
         │
         ▼
   Business Decisions
```

The scraper is therefore only the **ingestion layer**. The objective is to progressively transform collected data into reusable intelligence products.

---

# Current Product

The current pipeline targets **Shopify supplement storefronts**.

It:

* discovers and crawls configured Shopify storefronts
* attempts Shopify Storefront GraphQL where configured
* falls back to publicly exposed product catalog endpoints when required
* extracts product and variant information
* normalizes heterogeneous storefront responses
* captures pricing, discount, and inventory-related signals
* persists crawl snapshots
* deduplicates records across stores and crawl timestamps
* produces lightweight analytical outputs
* provides a foundation for longitudinal market intelligence

The current implementation is intentionally focused.

The goal is to establish a reliable **vertical intelligence pipeline** before expanding into additional e-commerce categories.

---

# Target Customers

The platform is designed around customers who can make economically meaningful decisions from Shopify market signals.

### 1. DTC brands

**Decision:**

> How does our assortment and pricing compare with competitors?

Potential intelligence:

* competitor products
* price positioning
* discounts
* product launches
* assortment changes
* inventory signals

---

### 2. E-commerce operators

**Decision:**

> What products and categories are moving in our niche?

Potential intelligence:

* new product detection
* product availability changes
* pricing movements
* category expansion
* assortment trends

---

### 3. Product and merchandising teams

**Decision:**

> What should we launch, promote, or remove?

Potential intelligence:

* product introductions
* assortment overlap
* pricing distribution
* discount frequency
* category activity

---

### 4. Competitive intelligence teams

**Decision:**

> What are competitors changing?

Potential intelligence:

* price changes
* new products
* discontinued products
* promotions
* inventory changes
* catalog expansion

---

### 5. Importers and product researchers

**Decision:**

> Which products or categories deserve further sourcing research?

Potential intelligence:

* emerging products
* pricing ranges
* product popularity proxies
* category expansion
* competitor assortment

The pipeline does not assume that every extracted field has commercial value. The objective is to identify which signals consistently support valuable decisions.

---

# Data Architecture

The platform follows a layered data architecture.

## Bronze — Raw Storefront Data

Bronze preserves what was observed from the source as closely as practical.

Examples:

```text
store_url
crawl_timestamp
source_endpoint
raw_product_payload
raw_variant_payload
```

The Bronze layer provides:

* traceability
* reproducibility
* debugging
* historical reconstruction
* source-level auditing

Raw data should not be treated as the final analytical dataset.

---

# Silver — Canonical E-commerce Data

The Silver layer converts heterogeneous Shopify responses into a consistent analytical model.

Conceptually:

```text
Store
 ├── Product
 │    ├── Variant
 │    │    ├── Price
 │    │    ├── Compare-at Price
 │    │    └── Inventory Signal
 │    │
 │    ├── Brand
 │    ├── Product Type
 │    ├── Tags
 │    ├── Images
 │    └── Collections
 │
 └── Crawl Snapshot
```

Representative entities include:

### Store

```text
store_id
store_url
domain
crawl_timestamp
```

### Product

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

### Variant

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

### Snapshot

```text
store_id
product_id
variant_id
crawl_timestamp
price
compare_at_price
availability
```

The snapshot model is particularly important because **a single crawl tells us what a store looks like now; repeated snapshots tell us how the market is changing.**

---

# Gold — Intelligence Products

The Gold layer is where raw e-commerce observations become business-facing datasets.

Potential Gold products include:

```text
gold/
├── pricing_intelligence/
├── product_intelligence/
├── inventory_intelligence/
├── promotion_intelligence/
├── assortment_intelligence/
├── competitor_intelligence/
└── market_intelligence/
```

### Pricing Intelligence

Answers:

> How are competitors pricing products in this niche?

Potential metrics:

* current price
* price range
* discount percentage
* price changes
* relative price positioning
* competitor price dispersion

---

### Product Intelligence

Answers:

> What products are entering or leaving the market?

Potential metrics:

* new product detection
* discontinued products
* product frequency
* assortment growth
* category expansion

---

### Inventory Intelligence

Answers:

> Which products are becoming unavailable?

Potential metrics:

* availability changes
* out-of-stock frequency
* availability duration
* product availability trends

Inventory signals should be treated as **observations**, not automatically interpreted as true inventory levels unless the source explicitly exposes reliable quantity data.

---

### Promotion Intelligence

Answers:

> How aggressively are competitors discounting?

Potential metrics:

* discount percentage
* promotional frequency
* products on promotion
* average discount by category
* promotion duration

---

### Assortment Intelligence

Answers:

> How does one store's product catalog compare with its competitors?

Potential metrics:

* category coverage
* overlapping products
* unique products
* brand concentration
* assortment expansion

---

### Competitor Intelligence

Answers:

> What changed across a monitored group of stores?

Potential signals:

```text
new product
price change
discount introduced
product removed
availability changed
assortment expanded
assortment contracted
```

This is where repeated snapshots become significantly more valuable than one-time scraping.

---

# Source Strategy

The platform begins with Shopify because Shopify storefronts provide a large and fragmented ecosystem of independent brands.

The longer-term source strategy is not simply:

```text
"Scrape more Shopify stores."
```

It is:

```text
More stores
      +
More snapshots
      +
More verticals
      +
More normalized signals
      =
Higher-value market intelligence
```

Potential vertical expansion includes:

```text
Shopify-Supplements/
Shopify-Pet-Products/
Shopify-Fashion/
Shopify-Beauty/
Shopify-Home-Goods/
Shopify-Electronics/
```

Each vertical should only be introduced when there is a clearly defined business question and identifiable customer value.

---

# Repository Structure

```text
.
├── Shopify-Supplements/
│   ├── pipeline.py
│   ├── engine.py
│   ├── graphql_client.py
│   ├── normalizer.py
│   ├── db_manager.py
│   ├── analytics.py
│   └── config.py
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

### Core components

| Component           | Responsibility                           |
| ------------------- | ---------------------------------------- |
| `pipeline.py`       | Pipeline orchestration                   |
| `engine.py`         | Async crawling and catalog retrieval     |
| `graphql_client.py` | Storefront GraphQL integration           |
| `normalizer.py`     | Canonical product/variant transformation |
| `db_manager.py`     | Persistence and schema management        |
| `analytics.py`      | Analytical transformations and reporting |
| `config.py`         | Runtime and source configuration         |
| `tests/`            | Automated validation                     |

---

# Data Quality Principles

A production-oriented intelligence pipeline must treat data quality as a first-class concern.

The pipeline should preserve:

### Source traceability

Every observation should be attributable to:

```text
source
store
crawl
timestamp
product
variant
```

### Deduplication

Records should not be duplicated simply because the same product appears across repeated crawls.

### Historical integrity

Historical observations should not be overwritten when the purpose is to measure change over time.

### Schema consistency

Different Shopify storefront responses should be normalized into a common canonical schema.

### Observability

Pipeline failures, source changes, request failures, and unexpected schema changes should be detectable.

---

# Installation

## 1. Create a virtual environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

## 2. Install dependencies

```powershell
pip install httpx
```

Optional analytical support:

```powershell
pip install pandas
```

---

# Configuration

Configure the target storefronts in:

```text
Shopify-Supplements/config.py
```

Current configuration includes:

```text
TARGET_STORES
STOREFRONT_TOKENS
MAX_CONCURRENCY
```

### `TARGET_STORES`

Defines the Shopify storefronts to monitor.

### `STOREFRONT_TOKENS`

Optional credentials used when Storefront GraphQL access is available.

### `MAX_CONCURRENCY`

Controls parallel request execution and should be tuned conservatively to maintain reliable collection.

---

# Running the Pipeline

```powershell
python Shopify-Supplements/pipeline.py
```

The current implementation produces:

```text
shopify_supplement_intelligence.json
shopify_intelligence.db
```

---

# Testing

Run the standard library test suite:

```powershell
python -m unittest discover tests
```

Or use pytest:

```powershell
pytest
```

The test suite covers the major pipeline components, including:

* crawling
* GraphQL client behavior
* normalization
* persistence
* analytics
* configuration
* orchestration

---

# From Scraper to Data Product

The current implementation is intentionally the beginning rather than the final architecture.

The evolution path is:

```text
Phase 1
Reliable Shopify ingestion
        ↓
Phase 2
Canonical Silver data model
        ↓
Phase 3
Historical snapshots
        ↓
Phase 4
Gold intelligence datasets
        ↓
Phase 5
Automated market monitoring
        ↓
Phase 6
Dashboards / APIs / alerts
```

The key transition is from:

```text
"What products exist?"
```

to:

```text
"What changed?"
```

and ultimately:

```text
"What decision should the customer make?"
```

---

# Roadmap

## Data Engineering

* [ ] Introduce a shared Shopify core package
* [ ] Separate Bronze, Silver, and Gold storage
* [ ] Formalize canonical schemas
* [ ] Add schema validation
* [ ] Add data quality checks
* [ ] Improve crawl observability
* [ ] Add structured run metadata
* [ ] Add configurable output locations
* [ ] Add CLI configuration
* [ ] Improve historical snapshot management

## Intelligence

* [ ] Price-change detection
* [ ] New-product detection
* [ ] Product removal detection
* [ ] Promotion detection
* [ ] Availability-change detection
* [ ] Assortment comparison
* [ ] Competitor benchmarking
* [ ] Category-level analytics
* [ ] Cross-store trend analysis

## Platform

* [ ] Expand beyond supplements
* [ ] Introduce shared vertical configurations
* [ ] Automate scheduled crawls
* [ ] Add Gold-layer data products
* [ ] Build analytics dashboards
* [ ] Expose selected intelligence through APIs
* [ ] Add alerting for significant market changes

---

# Design Principles

### 1. Business question before scraper

No source should be added simply because it is technically scrapeable.

The first question is:

> **Who needs this data, what decision does it support, and why would they pay for it?**

---

### 2. Historical data creates intelligence

A product catalog snapshot is useful.

A sequence of snapshots is much more valuable because it allows us to measure:

```text
Change
Velocity
Frequency
Direction
```

---

### 3. Normalize once, analyze many times

Source-specific extraction belongs in ingestion.

Business logic belongs downstream.

This allows the same Silver dataset to support multiple Gold products without rebuilding the crawler.

---

### 4. Gold should represent decisions

The Gold layer should not simply contain another copy of Silver.

It should answer questions such as:

```text
Which competitors changed prices?

Which products are newly available?

Which categories are expanding?

Which products are repeatedly discounted?

Which stores are changing their assortment?

Where are meaningful market shifts occurring?
```

---

### 5. Reliability before scale

A small number of high-quality, historically monitored stores is more valuable than thousands of poorly validated records.

Scale should follow proven data quality and customer value.

---

# End State

The long-term objective is to evolve this repository from a Shopify scraping project into a reusable **E-commerce Intelligence Platform**.

```text
                 E-COMMERCE SOURCES
                         │
        ┌────────────────┼────────────────┐
        │                │                │
     Shopify          Amazon          Marketplaces
        │                │                │
        └────────────────┼────────────────┘
                         ▼
                  BRONZE / RAW
                         │
                         ▼
                 SILVER / CANONICAL
                         │
             ┌───────────┼───────────┐
             ▼           ▼           ▼
          Products     Prices    Inventory
             │           │           │
             └───────────┼───────────┘
                         ▼
                    GOLD / INTELLIGENCE
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
     Pricing          Product          Market
  Intelligence     Intelligence     Intelligence
        │                │                │
        └────────────────┼────────────────┘
                         ▼
                  BUSINESS DECISIONS
```

The objective is not to build the world's largest Shopify scraper.

It is to build a **reliable data system that converts fragmented e-commerce storefront activity into decision-ready intelligence.**
