SHOPIFY INTELLIGENCE PIPELINE 
From fragmented Shopify storefront activity to decision-ready competitive intelligence

The Shopify Intelligence Pipeline is an end-to-end data engineering and intelligence platform designed to transform fragmented, fast-changing Shopify storefront activity into historical, explainable, decision-ready intelligence.

The initial vertical is supplements, where brands compete continuously across:

pricing
discounts
promotions
product assortment
product launches
availability
competitive positioning
customer perception
search visibility
social activity
advertising activity
geographic pricing
market trends

The problem is not a lack of e-commerce data.

The problem is that competitive signals are fragmented, ephemeral, difficult to compare historically, and disconnected from the business decisions they are supposed to support.

A competitor can change a price, launch a product, remove an SKU, run a promotion, experience an availability event, increase advertising activity, or change its market positioning without producing a clean analytical record.

This platform creates that record.

The objective is not to scrape Shopify stores. The objective is to build a reliable intelligence system that converts fragmented e-commerce activity into historical, explainable, decision-ready data — and ultimately delivers that intelligence to the businesses that need to act on it.

The Business Problem

A supplement brand monitoring competitors manually can answer:

What is this competitor selling right now?

But it struggles to answer:

What changed?

When did it change?

How significant was the change?

Which competitors are becoming more aggressive?

Which products are repeatedly discounted?

Which competitors are expanding their assortment?

Which products are becoming unavailable?

Which brands have stronger customer perception?

Which competitors are gaining search or social attention?

Which products have similar competitive positioning?

How are competitors positioning prices across markets?

What market patterns are emerging?

More importantly:

What should the business do about it?

That is the problem this architecture is designed to solve.

The Core Architecture

The system has evolved from a storefront crawler into a layered intelligence platform:

                         SHOPIFY STOREFRONTS
                                  │
                                  ▼
                         ┌──────────────────┐
                         │    INGESTION     │
                         │                  │
                         │ Async collection │
                         │ GraphQL          │
                         │ Catalog fallback │
                         │ Retries          │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │      BRONZE      │
                         │                  │
                         │ Raw observations │
                         │ Crawl metadata   │
                         │ Source evidence  │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │      SILVER      │
                         │                  │
                         │ Canonical model  │
                         │ Validation       │
                         │ Deduplication    │
                         │ Historical state │
                         └────────┬─────────┘
                                  │
                                  ▼
                    ┌─────────────────────────────┐
                    │         ENRICHMENT           │
                    │                             │
                    │ Internal product signals   │
                    │ External market context    │
                    │                             │
                    │ Reviews / Sentiment         │
                    │ Brand Reputation            │
                    │ SEO / Search                │
                    │ Social Engagement           │
                    │ Advertising                 │
                    │ Geographic Pricing          │
                    │ Competitor Similarity       │
                    │ Market Trends               │
                    └──────────────┬──────────────┘
                                   │
                                   ▼
                         ┌──────────────────┐
                         │       GOLD       │
                         │                  │
                         │ Pricing          │
                         │ Discounts        │
                         │ Inventory        │
                         │ Competition      │
                         │ Product activity │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │     SERVING      │
                         │                  │
                         │ Tenant APIs      │
                         │ Webhooks         │
                         │ Alerts           │
                         │ Operator plane   │
                         └────────┬─────────┘
                                  │
                                  ▼
                         BUSINESS DECISIONS

The architectural contract is:

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
    ↓
ACTION

Bronze preserves evidence. Silver creates trust. Enrichment adds context. Gold creates intelligence. Serving delivers that intelligence.

Architectural Separation of Concerns

A central design decision in this project is separating generation of intelligence from delivery of intelligence.

These are different engineering problems.

Intelligence Generation
Bronze
   ↓
Silver
   ↓
Enrichment
   ↓
Gold

This answers:

What intelligence should exist?

Intelligence Serving
Gold
   ↓
Serving API
   ↓
Merchant

This answers:

How does a customer consume that intelligence?

Event Delivery
Gold / Business Event
        ↓
Event Envelope
        ↓
Webhook Dispatcher
        ↓
Merchant Endpoint

This answers:

How does the customer receive a time-sensitive change?

Keeping these responsibilities separate prevents the analytical pipeline from becoming tightly coupled to customer delivery infrastructure.

Current Monitored Domain

The initial implementation focuses on the supplement e-commerce market.

Current monitored merchants include:

Transparent Labs
Kaged
GHOST Lifestyle
Cellucor
Gorilla Mind
PE Science

The architecture is intentionally designed so that the underlying intelligence model can eventually expand beyond supplements into broader e-commerce categories.

Bronze — Source Evidence

Bronze represents what the system actually observed.

Its responsibility is preservation and traceability, not interpretation.

Typical source metadata includes:

store_url
crawl_timestamp
source_endpoint
crawl_id
raw_product_payload
raw_variant_payload
extraction_status

Bronze exists so downstream transformations can be:

reproduced
audited
debugged
reprocessed
compared against source observations

The principle is:

Never destroy source evidence merely because a cleaner representation exists downstream.

Silver — Canonical E-commerce Dataset

Silver is the trust boundary between raw acquisition and intelligence generation.

The transformation is orchestrated through:

silver_supplements_orchestrator.py

The pipeline no longer follows:

Scrape
  ↓
Analytics

Instead:

Bronze
  ↓
Silver
  ↓
Enrichment
  ↓
Gold

Silver is responsible for:

validation
normalization
type standardization
canonical identity
deduplication
record integrity
historical representation

Conceptually:

                    BRONZE
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
      Raw Data      Metadata       Snapshots
        │              │              │
        └──────────────┼──────────────┘
                       ▼
        silver_supplements_orchestrator.py
                       │
             ┌─────────┼─────────┐
             ▼         ▼         ▼
        Validation  Identity  Normalization
             │         │         │
             └─────────┼─────────┘
                       ▼
                     SILVER

Silver establishes the canonical analytical contract used by everything downstream.

Data Integrity

During development, a duplicate-record issue was discovered in downstream analytical outputs.

The problem was fixed during pipeline hardening.

This is not a cosmetic correction.

Duplicate observations can distort:

product counts
discount rankings
pricing statistics
inventory analysis
competitor comparisons
historical trends
aggregate intelligence

The architectural rule is:

A business decision is only as trustworthy as the uniqueness, lineage, and temporal integrity of the data underneath it.

Therefore:

Raw evidence
    ↓
Canonical identity
    ↓
Validated record
    ↓
Historical observation

is established before intelligence products are generated.

Historical Data Is a First-Class Product

A current product record tells us:

What exists now?

A historical snapshot tells us:

What existed at a particular point in time?

A sequence of observations tells us:

What changed?

The intelligence model therefore follows:

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

This temporal model is one of the most important foundations of the platform.

Enrichment Layer

The enrichment layer adds context around trusted Silver observations.

It deliberately separates:

INTERNAL ENRICHMENT
        +
EXTERNAL ENRICHMENT
        ↓
ENRICHED INTELLIGENCE

Architecture:

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
Internal Pricing Intelligence

The internal pricing foundation is derived from actual Shopify observations.

Current enrichment foundation:

shopify_supplements_enrichment/
└── pricing_enrichment/
    └── price_metrics.json

Core fields include:

sku
product_title
store_url
current_price

The architectural relationship is:

Shopify Storefront
       ↓
Bronze
       ↓
Silver
       ↓
Price Metrics
       ↓
Internal Intelligence

This provides an authoritative product and pricing foundation for downstream enrichment.

External Intelligence

The external enrichment architecture is implemented through:

external_enricher.py

and:

api_clients.py

The enrichment domains are organized as:

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

The enrichment framework has been executed across:

2,059 base SKUs

External Provider Architecture

External intelligence is deliberately decoupled from the enrichment orchestrator.

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

The client layer provides:

environment-driven credentials
provider abstraction
modular API integration
HTTP transport
separation between acquisition and enrichment logic

This means the intelligence model does not need to be redesigned every time an external provider changes.

External Intelligence Domains
Customer Reviews & Sentiment
external_enrichment/customer_reviews/

Potential intelligence:

rating
review_count
positive_sentiment
negative_sentiment
review_text

Business question:

How are customers perceiving competing products and brands?

Brand Reputation & Positioning
external_enrichment/brand_reputation/

Potential signals:

brand
reputation_score
brand_position
market_presence

Business question:

How does brand perception relate to competitive positioning?

SEO & Search Visibility
external_enrichment/seo_search/

Potential signals:

primary_keyword
search_volume
search_activity
search_visibility

Business question:

Which products and brands are gaining search attention?

Social Engagement
external_enrichment/social_engagement/

Potential signals:

engagement
reach
social_activity
viral_coefficient

Business question:

Which products and brands are generating external attention?

Advertising Intelligence
external_enrichment/ad_intelligence/

Potential signals:

ad_count
advertising_activity
product_ad_presence
competitive_ad_pressure

Business question:

Where is competitive promotional pressure increasing?

Geographic Pricing
external_enrichment/geographical_arbitrage/

Potential signals:

domestic_price
uk_price
eu_price
regional_price_spread
currency_effect
arbitrage_signal

Business question:

How are competitors positioning products across geographic markets?

Competitor Similarity
external_enrichment/competitor_similarity/

Potential signals:

product_similarity
competitor_similarity_score
category_overlap
price_similarity
assortment_overlap

Analytical progression:

Product
   ↓
Similar Products
   ↓
Competitive Set
   ↓
Competitor Benchmark
Market Trends
external_enrichment/market_trends/

Potential signals:

category_trend
market_activity
pricing_trend
demand_proxy
competitive_pressure
trend_velocity

Business question:

What is happening beyond an individual product or merchant?

Enrichment Provenance

The system explicitly distinguishes between different classes of intelligence.

OBSERVED
   ↓
Directly observed from source data

DERIVED
   ↓
Calculated from trusted observations

EXTERNAL
   ↓
Retrieved from external providers

SIMULATED
   ↓
Generated by fallback logic when live
provider data is unavailable

The verified enrichment execution used the fallback simulation engine to generate and persist all eight enrichment domains across the 2,059-SKU foundation.

That is an architectural validation step — not a claim that simulated metrics are live market observations.

The distinction is critical:

A data product must never present simulated intelligence as externally observed intelligence.

Gold — Decision-Ready Data Products

Gold is where the architecture changes from data engineering to decision engineering.

Silver asks:

What did we observe?

Enrichment asks:

What context surrounds the observation?

Gold asks:

What does the evidence mean for a business decision?

Therefore Gold is organized around business questions, not merely source tables.

Gold Architecture

The current Gold design centers on merchant-specific decision products.

Conceptually:

                         SILVER
                           +
                      ENRICHMENT
                           │
                           ▼
                 Canonical Merchant/Product
                       Feature Layer
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
      Pricing          Inventory        Discounts
     Intelligence      Intelligence     Intelligence
          │                │                │
          └────────────────┼────────────────┘
                           ▼
                 Competitive Intelligence
                           │
                           ▼
                          GOLD

The current Gold serving boundary is organized under:

Gold_Lake/
└── Pricing_Intelligence/
    └── Shopify_Merchants/

The design principle is:

A Gold dataset should answer a specific customer question and make the resulting decision easier, faster, and more defensible.

Gold Product: Pricing Opportunities
product_pricing_opportunities/

This product answers:

Where are pricing opportunities or anomalies that a merchant should investigate?

Potential intelligence includes:

current_price
competitor_price
price_difference
relative_price_position
discount_pressure
pricing_signal

Serving endpoint:

GET /api/v1/merchants/{merchant_id}/pricing-opportunities
Gold Product: Inventory Risk
inventory_risk/

This product answers:

Which products present potential availability or inventory risks?

The system deliberately treats storefront availability as a signal rather than claiming that storefront observations are exact warehouse inventory.

Serving endpoint:

GET /api/v1/merchants/{merchant_id}/inventory-risks
Gold Product: Discount Opportunities
discount_opportunities/

This product answers:

Where is promotional or discount activity creating a competitive opportunity or threat?

Potential intelligence:

discount_percentage
competitor_discount
discount_spread
promotion_pressure
discount_signal

Serving endpoint:

GET /api/v1/merchants/{merchant_id}/discount-opportunities
Gold Product: Competitive Intelligence
competitive_intelligence/

This product combines multiple competitive dimensions.

Potential inputs include:

pricing
discounts
availability
assortment
product activity
customer perception
search visibility
social activity
advertising
geographic pricing
competitor similarity
market trends

Serving endpoint:

GET /api/v1/merchants/{merchant_id}/competitive-intelligence

This represents the transition from individual metrics to merchant-level competitive intelligence.

Merchant-Centric Gold Architecture

The serving model is intentionally merchant-centric.

Instead of exposing a generic dataset and forcing customers to understand the underlying schema:

Raw Dataset
     ↓
Customer must interpret it

the architecture moves toward:

Merchant
   ↓
Business Question
   ↓
Decision Product
   ↓
Action

For example:

Merchant
   ↓
"Where should I investigate pricing?"
   ↓
Pricing Opportunities
   ↓
Pricing decision

This is the fundamental reason Gold is organized around data products, rather than simply analytical tables.

Serving Layer

Today's major architectural addition is the Merchant Serving Layer.

The implementation is a FastAPI service that sits between Gold Parquet data and downstream merchants.

                         GOLD LAKE
                            │
                            ▼
                  Merchant Serving API
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
          Pricing       Inventory       Discounts
       Opportunities       Risks       Opportunities
             │              │              │
             └──────────────┼──────────────┘
                            ▼
                  Competitive Intelligence
                            │
                            ▼
                       MERCHANT

The serving application is currently:

Merchants_serving.py

Current service version:

2.4.3
Why Serving Is Separate From Gold Generation

Gold generation and serving have different operational characteristics.

Gold generation

Concerned with:

correctness
transformations
joins
enrichment
business logic
historical consistency
analytical reproducibility
Serving

Concerned with:

authentication
tenant isolation
API contracts
latency
delivery
retries
event signatures
operational health
customer consumption

Therefore:

GOLD
  │
  │ analytical contract
  ▼
SERVING
  │
  ├── API
  ├── Webhooks
  ├── Alerts
  └── Integrations

This separation allows Gold to remain an analytical system while Serving becomes an operational system.

Multi-Tenant Serving

The current serving architecture defines merchant tenants explicitly.

Current tenant configuration includes:

merchant_001 → Transparent Labs
merchant_002 → Kaged
merchant_003 → Ghost Lifestyle
merchant_004 → Cellucor
merchant_005 → Gorilla Mind
merchant_006 → PE Science

Each tenant has:

merchant_id
name
store_url
api_key
webhook_endpoint
webhook_secret

The API uses the merchant identifier to establish the tenant context.

The critical isolation rule is:

Request
  ↓
merchant_id
  ↓
authentication
  ↓
tenant configuration
  ↓
tenant store_url
  ↓
Gold query

A merchant therefore cannot simply request another merchant's Gold records by changing an API parameter.

Tenant Authentication

The serving API uses an API-key-based tenant authentication mechanism.

The access path is:

Client Request
      │
      ▼
X-API-Key
      │
      ▼
merchant_id
      │
      ▼
Tenant Lookup
      │
      ▼
Constant-Time Credential Comparison
      │
      ▼
Authorized Gold Access

Credential comparison uses:

hmac.compare_digest(...)

to avoid ordinary string comparison for secret validation.

Unauthorized requests are rejected before Gold data is returned.

Gold Data Access Layer

The serving API reads Gold Parquet datasets through:

ParquetStoreReader

The reader:

resolves the requested Gold category
loads the corresponding Parquet dataset
validates the presence of store_url
filters records to the authenticated tenant
returns the tenant-specific records

Conceptually:

Gold Parquet
     │
     ▼
ParquetStoreReader
     │
     ▼
store_url filter
     │
     ▼
Tenant Dataset
     │
     ▼
API Response

This keeps the serving layer from exposing the entire Gold lake to a merchant.

Merchant API

Current API endpoints include:

GET /

Service health/root response.

GET /api/v1/merchants/{merchant_id}/pricing-opportunities

Pricing intelligence.

GET /api/v1/merchants/{merchant_id}/inventory-risks

Inventory risk intelligence.

GET /api/v1/merchants/{merchant_id}/discount-opportunities

Discount intelligence.

GET /api/v1/merchants/{merchant_id}/competitive-intelligence

Competitive intelligence.

GET /api/v1/merchants/{merchant_id}/health

Tenant-specific webhook health.

Webhook Serving

The serving architecture also introduces an operational delivery mechanism for business events.

The webhook dispatcher creates a canonical event envelope containing:

event_id
event_type
event_version
occurred_at
merchant_id
entity_type
entity_id
source
data

Example conceptual event:

Gold Intelligence
       ↓
Business Event
       ↓
Event Envelope
       ↓
Webhook Dispatcher
       ↓
Merchant Endpoint

The event structure is designed to create a stable contract between the intelligence platform and downstream merchant systems.

Event Identity

Each webhook event receives a unique identifier:

evt_<unique-id>

Each delivery attempt receives its own delivery identifier:

del_<unique-id>

The event ID is also used as the idempotency key:

X-Idempotency-Key

This allows the receiving system to distinguish:

same event
     vs.
different delivery attempt

That distinction becomes important when retries occur.

Webhook Security

Webhook payloads are signed using:

HMAC-SHA256

The signature is generated from the serialized event envelope and a tenant-specific webhook secret.

The request contains:

X-Webhook-Id
X-Event-Id
X-Webhook-Timestamp
X-Webhook-Signature
X-Idempotency-Key

Conceptually:

Event Envelope
      │
      ▼
Canonical JSON
      │
      +
Tenant Webhook Secret
      │
      ▼
HMAC-SHA256
      │
      ▼
Webhook Signature

This establishes a cryptographic mechanism for downstream consumers to verify that a webhook was generated using the configured tenant secret.

Webhook Reliability

The dispatcher implements retry handling for unsuccessful deliveries.

Current configuration:

Maximum retries: 5
Base backoff:    2 seconds
Timeout:         5 seconds

Retry behavior uses exponential backoff with jitter:

Attempt 1
   ↓
2s + jitter

Attempt 2
   ↓
4s + jitter

Attempt 3
   ↓
8s + jitter

Attempt 4
   ↓
16s + jitter

Attempt 5
   ↓
Dead Letter Queue

This prevents a temporarily unavailable merchant endpoint from immediately becoming a permanent delivery failure.

Dead-Letter Queue

After all retry attempts fail, the event is moved into an in-memory dead-letter queue.

The DLQ captures:

event_id
delivery_id
merchant_id
event_type
payload
error
failed_at

This creates an explicit failure state:

Event
  ↓
Delivery
  ↓
Retry
  ↓
Retry
  ↓
Retry
  ↓
Retry
  ↓
Retry
  ↓
DEAD LETTER

The architectural principle is:

A failed delivery should become an observable state, not a silently lost event.

Delivery Observability

The webhook engine maintains delivery logs containing:

delivery_id
event_id
merchant_id
event_type
status
attempts
error
timestamp

Successful deliveries are recorded as:

SUCCESS

Failed exhausted deliveries are recorded as:

DEAD_LETTER

The system also tracks endpoint health per merchant.

This provides the foundation for future operational metrics such as:

delivery_success_rate
retry_rate
dead_letter_rate
endpoint_availability
average_delivery_latency
Operator Plane

The serving architecture now includes a separate operator endpoint:

GET /api/v1/internal/system/webhook-logs

This endpoint exposes:

active_dead_letter_count
dead_letter_queue
recent_delivery_logs

Access is protected by an operator API key.

The conceptual separation is:

MERCHANT PLANE
      │
      ├── Gold data
      ├── Business intelligence
      └── Merchant webhooks

OPERATOR PLANE
      │
      ├── Delivery logs
      ├── Dead letters
      ├── Endpoint health
      └── Operational diagnostics

This prevents operational diagnostics from being treated as ordinary merchant-facing data.

Current Event Architecture

The current serving layer supports manual test-event triggering through:

POST /api/v1/webhooks/trigger-test-event

The current flow is:

API Request
    ↓
Tenant Authentication
    ↓
Test Business Event
    ↓
Background Task
    ↓
Webhook Dispatcher
    ↓
Signed HTTP Request
    ↓
Merchant Endpoint

This is currently a serving/integration test capability.

The next architectural step is to replace manual triggering with automated business-event detection derived from Gold changes.

The target architecture is:

Gold
  ↓
Business Event Detector
  ↓
Canonical Event
  ↓
Durable Queue
  ↓
Webhook Worker
  ↓
Retry / Signing / DLQ
  ↓
Merchant

This distinction is important:

The current implementation proves the delivery mechanism. It does not yet claim that every Gold change automatically produces an event.

Current Gold-to-Serving Boundary

The platform now has two distinct paths:

Analytical path
Bronze
   ↓
Silver
   ↓
Enrichment
   ↓
Gold
Consumption path
Gold
   ↓
Serving Adapter
   ↓
FastAPI
   ├── REST APIs
   ├── Webhooks
   └── Health

This creates a clean architectural boundary:

                 DATA PLATFORM
                      │
       ┌──────────────┴──────────────┐
       ▼                             ▼
   Generation                    Serving
       │                             │
   Bronze                         FastAPI
       ↓                             │
   Silver                            ├── API
       ↓                             ├── Webhooks
 Enrichment                          ├── Alerts
       ↓                             └── Integrations
     Gold
Why the Serving Layer Matters

Generating intelligence is only half of the problem.

A Gold dataset sitting on disk does not automatically create customer value.

A customer needs to be able to consume:

"What changed?"
"Where is the opportunity?"
"Which competitor moved?"
"What requires attention?"

without understanding:

Parquet
pandas
enrichment folders
pipeline internals
scraper implementation
data transformations

That is why serving exists.

Gold is the decision-ready data contract. Serving is the delivery contract.

From Data Engineering to Decision Engineering

The architecture increasingly follows:

SOURCE
  ↓
OBSERVATION
  ↓
CANONICAL DATA
  ↓
ENRICHMENT
  ↓
DECISION SIGNAL
  ↓
BUSINESS EVENT
  ↓
DELIVERY
  ↓
ACTION

For example:

Competitor changes price
        ↓
Silver captures historical state
        ↓
Gold calculates price movement
        ↓
Competitive intelligence identifies significance
        ↓
Business event generated
        ↓
Webhook delivered
        ↓
Merchant investigates pricing

This is the intended direction of the platform.

Data Products vs Data Tables

The platform deliberately avoids treating Gold as a collection of generic analytical tables.

A Gold product should answer:

Who is this for?

What painful question does it answer?

What decision does it support?

Why is the information valuable enough to pay for?

Therefore:

Data
  ↓
Signal
  ↓
Decision Product
  ↓
Customer Outcome

is more important than:

Data
  ↓
Table
  ↓
Dashboard
Current Repository Structure

The repository is evolving toward explicit separation of responsibilities:

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
├── Gold_Lake/
│   └── Pricing_Intelligence/
│       └── Shopify_Merchants/
│
├── shopify/
│   └── pipeline.py
│
├── tests/
│
├── shopify_intelligence.db
├── shopify_supplement_intelligence.json
└── README.md

The exact Gold product structure will continue to evolve as more decision products are productionized.

Component Responsibilities
Component	Responsibility
engine.py	Async storefront collection
graphql_client.py	Shopify Storefront GraphQL access
normalizer.py	Canonical product and variant transformation
db_manager.py	Persistence and database management
pipeline.py	End-to-end ingestion orchestration
silver_supplements_orchestrator.py	Bronze → Silver transformation
external_enricher.py	External intelligence orchestration
api_clients.py	External provider integration gateway
Gold orchestrators	Decision-product generation
Merchants_serving.py	Gold serving and merchant API
ParquetStoreReader	Tenant-filtered Gold access
WebhookDispatcher	Event delivery, retries and DLQ
tests/	Automated validation
Data Quality & Observability

Competitive intelligence is a decision-support product.

Incorrect data can therefore become an incorrect business decision.

The platform prioritizes:

Uniqueness

Prevent duplicate observations from corrupting metrics.

Completeness

Validate required product, merchant, source, and timestamp fields.

Consistency

Normalize heterogeneous storefront representations.

Historical Integrity

Preserve observations across runs.

Lineage

Trace intelligence back to source observations.

Provenance

Distinguish:

Observed
Derived
External
Simulated
Pipeline Observability

Track:

run_id
crawl_timestamp
source
records_extracted
records_valid
records_rejected
processing_duration
errors
Enrichment Observability

Track:

enrichment_domain
base_sku_count
records_enriched
provider
fallback_used
execution_status
Serving Observability

Track:

merchant_id
event_id
delivery_id
event_type
delivery_status
attempt_count
endpoint_health
dead_letter_count
timestamp
What Was Completed
Ingestion
 Async Shopify storefront crawling
 Concurrent multi-store collection
 Shopify Storefront GraphQL support
 Public catalog fallback
 Product extraction
 Variant extraction
 Pricing extraction
 Availability extraction
Bronze
 Raw source preservation
 Crawl metadata
 Source traceability
 Historical observations
Silver
 Silver architecture
 silver_supplements_orchestrator.py
 Canonical product model
 Validation
 Normalization
 Deduplication
 Historical snapshots
 Duplicate-record issue identified and fixed
Internal Enrichment
 Pricing enrichment
 Real Shopify pricing foundation
 price_metrics.json
 SKU-level enrichment foundation
External Enrichment
 external_enricher.py
 api_clients.py
 Environment-driven credentials
 Modular provider architecture
 HTTP transport layer
 Import/path execution issue resolved
 Full enrichment suite executed
 2,059 base SKUs processed
 Customer sentiment intelligence
 Brand reputation intelligence
 SEO/search intelligence
 Social intelligence
 Advertising intelligence
 Geographic pricing intelligence
 Competitor similarity
 Market trends
 JSON assets persisted
Gold
 Gold lake established
 Merchant/product intelligence model established
 Pricing opportunities product
 Inventory risk product
 Discount opportunities product
 Competitive intelligence product
 Gold Parquet serving boundary established
Serving
 FastAPI serving layer
 Versioned API structure
 Multi-tenant merchant model
 Tenant API-key authentication
 Constant-time credential comparison
 Tenant-isolated Gold queries
 Pricing opportunity endpoint
 Inventory risk endpoint
 Discount opportunity endpoint
 Competitive intelligence endpoint
 Tenant health endpoint
 Webhook dispatcher
 HMAC-SHA256 webhook signatures
 Event IDs
 Delivery IDs
 Idempotency keys
 Retry handling
 Exponential backoff
 Jitter
 Timeout handling
 Dead-letter handling
 Delivery logging
 Endpoint health tracking
 Secured operator endpoint
 Manual webhook test-event capability
Current Engineering Position

The project has moved through several architectural stages:

Stage 1
Shopify Scraper
      ↓

Stage 2
Historical Data Pipeline
      ↓

Stage 3
Bronze → Silver Data Platform
      ↓

Stage 4
Internal + External Enrichment
      ↓

Stage 5
Gold Decision Products
      ↓

Stage 6
Merchant Serving Layer

The current system is therefore better described as:

A multi-layer e-commerce intelligence platform with a merchant-facing serving boundary.

The crawler is now only one component.

What Is Not Yet Production-Complete

The serving layer is an architectural foundation, not yet a fully hardened production platform.

Remaining work includes:

External intelligence
 Production provider credentials
 Live external observations
 Provider-level lineage
 Source freshness monitoring
 Enrichment confidence scoring
Gold
 Automated Gold generation orchestration
 Cross-domain scoring
 Gold data quality contracts
 Product-level lineage into Gold
 Automated change detection
Eventing
 Automated Gold-derived event detection
 Durable event queue
 Dedicated webhook worker
 Persistent DLQ
 Persistent delivery logs
 Event replay mechanism
 Webhook timestamp/replay protection
 Production endpoint verification
Serving
 Production-grade secret management
 Persistent authentication store
 Rate limiting
 API request observability
 API version migration strategy
 Production deployment
 Horizontal scaling strategy

The important distinction is:

The architecture has been established; production hardening remains a separate engineering phase.

Roadmap
Phase 1 — Ingestion
 Multi-store asynchronous collection
 Shopify endpoint handling
 Product and variant extraction
 Historical persistence
Phase 2 — Silver
 Canonical data model
 Silver orchestration
 Deduplication
 Data integrity controls
 Historical snapshots
Phase 3 — Enrichment
 Internal pricing enrichment
 External enrichment architecture
 Customer sentiment
 Brand reputation
 SEO/search visibility
 Social engagement
 Advertising intelligence
 Geographic pricing
 Competitor benchmarks
 Market trends
 External API client architecture
 Fallback enrichment execution
 2,059-SKU enrichment run
Phase 4 — Gold
 Pricing opportunities
 Inventory risk
 Discount opportunities
 Competitive intelligence
 Cross-domain competitor scoring
 Automated Gold orchestration
 Gold data quality contracts
 Automated change detection
Phase 5 — Serving
 Gold Parquet serving
 Tenant-isolated API
 Merchant authentication
 Pricing API
 Inventory API
 Discount API
 Competitive intelligence API
 Tenant health
 Webhook dispatcher
 HMAC signing
 Retry/backoff
 Dead-letter handling
 Operator observability
 Durable event queue
 Automated Gold-derived events
 Production deployment
Phase 6 — Production External Intelligence
 Production Apify integrations
 Production Bright Data integrations
 Production DataForSEO integrations
 Production Meta Ad Library integration
 Live review intelligence
 Live search intelligence
 Live social intelligence
 Live advertising intelligence
 Live geographic pricing
 Provider reliability scoring
 Source freshness monitoring
Phase 7 — Intelligence Products
 Competitive pricing dashboard
 Promotion intelligence
 Product launch alerts
 Inventory alerts
 Competitor scorecards
 Market intelligence reports
 Merchant-specific intelligence feeds
Phase 8 — Platform Expansion
 Additional Shopify verticals
 Additional e-commerce sources
 Cross-marketplace intelligence
 Cross-platform product identity
 Broader e-commerce intelligence platform
Design Principles
1. Business Question Before Source

A source should not be added merely because it can be scraped.

Ask:

Who needs this information?

What decision does it support?

What pain does it remove?

Why should someone pay for it?

2. Raw Data Is Evidence

Bronze preserves what happened.

3. Silver Is the Analytical Contract

Silver provides the stable, canonical representation that downstream systems can trust.

4. Enrichment Adds Context
Observation
    ↓
Derived Signal
    ↓
External Context
    ↓
Intelligence Vector
5. Gold Represents Decisions

Gold should answer:

What changed?

Who changed it?

How significant was the change?

How does it compare with competitors?

What external signals surround the change?

What market pattern is emerging?

What should the business investigate or act on?
6. Serving Is a Separate Contract

Gold defines:

What intelligence exists?

Serving defines:

How that intelligence is consumed.

7. Provenance Is Non-Negotiable

The platform must preserve the difference between:

Observed
Derived
External
Simulated
8. Historical Data Is a Product
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
9. Reliability Before Scale

The goal is not to collect millions of records merely to demonstrate scraping scale.

The goal is:

Trustworthy, explainable signals that survive repeated pipeline runs and support real decisions.

10. Separate Acquisition From Intelligence
Crawler
   ↓
Evidence

Silver
   ↓
Trust

Enrichment
   ↓
Context

Gold
   ↓
Decision

Serving
   ↓
Delivery

Each layer has a different responsibility.

That separation is intentional.

Long-Term Vision

The long-term objective is to evolve the project from a Shopify-specific intelligence pipeline into an E-commerce Intelligence Platform.

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
                         ▼
                     SERVING
                         │
            ┌────────────┼────────────┐
            ▼            ▼            ▼
           APIs        Webhooks      Alerts
            │            │            │
            └────────────┼────────────┘
                         ▼
                  BUSINESS ACTIONS

The strategic progression is:

Scraping
   ↓
Data Collection
   ↓
Historical Intelligence
   ↓
Decision Products
   ↓
Operational Delivery
   ↓
E-commerce Intelligence Platform

The platform is therefore no longer being designed as a scraper with analytics attached.

It is being designed as a data product system.

The crawler collects the evidence.

Bronze preserves it.

Silver makes it trustworthy.

Enrichment adds context.

Gold makes it decision-ready.

Serving makes it consumable.

Events make it actionable.

And the customer ultimately pays for the decision, not the dataset.