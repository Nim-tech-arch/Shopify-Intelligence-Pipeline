# Shopify Supplements Intelligence Pipeline (SSIP)

> **A domain-engineered data and intelligence pipeline for Shopify supplement, sports nutrition, and wellness brands.**

SSIP — **Shopify Supplements Intelligence Pipeline** — is a production-oriented data infrastructure and commercial intelligence system built for extracting, normalizing, enriching, and serving decision-ready intelligence from Shopify supplement storefronts and related market signals.

SSIP is designed around a simple principle:

> **Do not collect e-commerce data merely because it is available. Collect and transform it because it answers a commercial question.**

The pipeline converts raw storefront observations and external market signals into structured intelligence covering pricing, inventory, discounts, product variants, customer sentiment, SEO visibility, paid advertising, social activity, geographic pricing, competitor similarity, and market trends.

---

## 1. What SSIP Does

SSIP addresses the fragmentation that exists in supplement-market intelligence.

Generic e-commerce monitoring can identify a price or product change, but supplement products require additional context:

* servings versus container size
* price per serving
* ingredient-level economics
* flavor and variant changes
* subscription and bundle structures
* hidden promotional discounts
* stock availability
* review sentiment
* paid advertising activity
* organic search visibility
* social and influencer activity
* geographic pricing differences
* competitive product similarity

SSIP therefore operates as a layered intelligence pipeline:

```text
Shopify Storefronts
       │
       ▼
┌──────────────────────┐
│ Ingestion & Capture  │
│ Async Storefront API │
│ GraphQL / HTTP       │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Bronze Lake          │
│ Raw Historical State │
│ Provenance & Evidence│
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Silver Lake          │
│ Canonical Product    │
│ Variant & SKU Model  │
└──────────┬───────────┘
           │
           ▼
┌────────────────────────────┐
│ Supplement Enrichment      │
│                            │
│ Pricing                   │
│ Reviews & Sentiment       │
│ SEO                       │
│ Paid Ads                  │
│ Social                    │
│ Geographic Arbitrage      │
│ Brand Reputation          │
│ Competitor Similarity     │
│ Market Trends             │
└──────────┬─────────────────┘
           │
           ▼
┌──────────────────────┐
│ Gold Lake            │
│ Commercial Data      │
│ Products             │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Multi-Tenant API     │
│ FastAPI              │
│ Authentication       │
│ Tenant Isolation     │
└──────────────────────┘
```

---

# 2. Intelligence Domains

SSIP currently organizes enrichment around the following commercial domains:

### Pricing & Unit Economics

Normalizes supplement pricing across:

* servings
* container weights
* variants
* bundles
* subscriptions
* promotional prices

This enables analysis beyond the displayed MSRP.

### Inventory Intelligence

Tracks product availability and stockout events that can represent competitive opportunities.

### Discount Intelligence

Captures:

* sale pricing
* promotional cadence
* compare-at pricing
* subscription discounts
* gift-with-purchase signals

### Customer Review Intelligence

Extracts review-related signals including:

* review velocity
* sentiment
* recurring product feedback
* taste
* mixability
* clumping
* delivery
* other domain-specific themes

### SEO & Search Intelligence

Supports analysis of:

* target keywords
* search volume
* search intent
* organic ranking
* organic visibility

### Paid Advertising Intelligence

Tracks available signals around:

* active creative variations
* advertising platforms
* creative longevity
* advertising velocity

### Social & Influencer Intelligence

Provides structured signals around:

* social presence
* follower reach
* influencer activity
* engagement volume

### Geographic Arbitrage

Supports cross-market pricing analysis across currencies and geographic markets.

### Brand Intelligence

Provides structured information about:

* market positioning
* category tier
* brand characteristics
* competitive positioning

### Competitor Similarity

Maps potentially substitutable products using product/formula/ingredient and use-case similarity.

### Market Trends

Tracks emerging category and ingredient-level market signals.

---

# 3. Architecture

SSIP uses a Bronze → Silver → Enrichment → Gold → Serving architecture.

## 3.1 Bronze — Raw Market Provenance

The Bronze layer preserves point-in-time storefront observations.

Its purpose is to retain the raw evidence from which downstream transformations are derived.

Bronze data should preserve sufficient provenance to answer:

> What did we observe, from which source, and when?

The pipeline's provenance model distinguishes between:

```text
OBSERVED
EXTERNAL
SIMULATED
```

These classifications should remain visible throughout downstream processing.

---

## 3.2 Silver — Canonical Supplement Model

The Silver layer transforms raw storefront structures into normalized supplement-market entities.

Responsibilities include:

* product normalization
* variant normalization
* SKU identity
* serving normalization
* container-size normalization
* bundle separation
* subscription separation
* historical state tracking
* price normalization

SSIP uses longitudinal modeling to preserve changes in product and pricing state over time.

---

## 3.3 Supplement Enrichment Layer

The enrichment layer combines canonical product records with additional commercial signals.

Current enrichment domains include:

```text
pricing_enrichment/
external_enrichment/
├── customer_reviews/
├── brand_reputation/
├── seo_search/
├── social_engagement/
├── ad_intelligence/
├── geographical_arbitrage/
├── competitor_similarity/
└── market_trends/
```

The enrichment layer should not overwrite the underlying observations.

Enrichment results are derived intelligence and must remain distinguishable from source observations.

---

## 3.4 Gold — Commercial Data Products

The Gold layer contains business-ready datasets.

Current conceptual products include:

```text
pricing_opportunities/
inventory_intelligence/
discount_opportunities/
competitive_intelligence/
```

Gold datasets are optimized for downstream applications, analytics, APIs, and decision-support workflows.

---

# 4. Multi-Tenant Serving API

SSIP exposes selected intelligence through a FastAPI serving layer.

The serving architecture provides:

* tenant-aware access
* API-key authentication
* merchant scoping
* store-domain authorization
* structured JSON responses
* webhook integration

The current security model uses:

```text
x-api-key
```

with constant-time key comparison.

Tenant access must remain scoped to the authorized:

```text
merchant_id
store domain
```

A request must never be allowed to retrieve another tenant's data merely by modifying a request parameter.

---

# 5. API Contract

The production API should be treated as a versioned contract.

Recommended namespace:

```text
/api/v1/
```

The exact routes must correspond to the implementation in `app/main.py`.

Before deployment, verify that the README and implementation agree on:

* HTTP methods
* endpoint paths
* authentication requirements
* query parameters
* pagination
* filtering
* response models
* error responses
* tenant behavior
* rate limits

FastAPI automatically provides OpenAPI-based interactive API documentation when enabled.

Expected documentation endpoints are typically:

```text
/docs
/redoc
/openapi.json
```

These should be verified against the deployed application rather than assumed.

---

# 6. Example Intelligence Response

A representative SSIP response can contain canonical product information combined with commercial intelligence:

```json
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

      "social_followers_total": 85000
    }
  ]
}
```

The values above represent the README's example payload. They should not be interpreted as guaranteed current production values.

---

# 7. Webhook Event Engine

SSIP supports an event-delivery architecture for downstream automation.

The webhook subsystem provides:

### HMAC-SHA256 signatures

Webhook payloads are signed so receiving systems can verify authenticity.

### Retry and backoff

Failed deliveries are retried using exponential backoff with jitter.

### Dead-Letter Queue

Events that cannot be successfully delivered are retained for operational review rather than silently discarded.

### Idempotency

Webhook events contain an idempotency identifier to protect downstream systems from duplicate processing.

The implementation is located under:

```text
app/webhooks.py
```

---

# 8. Repository Structure

```text
.
├── Shopify-Supplements/
│   ├── pipeline.py
│   ├── engine.py
│   ├── graphql_client.py
│   ├── normalizer.py
│   ├── db_manager.py
│   └── silver_supplements_orchestrator.py
│
├── shopify_supplements_enrichment/
│   ├── pricing_enrichment/
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
│
├── app/
│   ├── main.py
│   ├── security.py
│   └── webhooks.py
│
└── README.md
```

The repository structure should remain synchronized with the actual implementation.

---

# 9. System Requirements

Before deployment, verify the repository's dependency/configuration files for the authoritative runtime requirements.

At minimum, the production environment must provide:

* supported Python runtime
* dependency installation mechanism
* persistent data storage appropriate for Bronze/Silver/Gold data
* network access to required external services
* secure environment-variable/secret configuration
* production ASGI serving
* HTTPS at the deployment boundary

**Do not infer the Python version from this README.** The version declared by the repository's dependency/runtime configuration is authoritative.

---

# 10. Dependency Management

Production dependencies must be declared in the repository's dependency manifest.

Supported examples include:

```text
requirements.txt
pyproject.toml
uv.lock
```

Use the dependency mechanism actually present in the repository.

Dependencies should be pinned or lock-resolved for reproducible deployments. FastAPI's own deployment documentation recommends pinning the FastAPI version used by a production application so it remains compatible with the rest of the system.

Do not install undocumented packages manually on the production server.

---

# 11. Environment Configuration

Production secrets must never be committed to Git.

Create an example configuration file such as:

```text
.env.example
```

The actual variable names must match those implemented by the application.

At minimum, document configuration categories for:

```text
Application environment
API authentication
Shopify credentials
External enrichment services
Storage/data paths
Webhook signing
CORS / allowed origins
Logging
```

Example structure:

```env
APP_ENV=production

API_KEY=<secret>

# Shopify / external integrations
# SHOPIFY_...
# EXTERNAL_...

# Storage
# DATA_...

# Webhooks
# WEBHOOK_...
```

**Do not put real credentials in `.env.example`, README files, Git history, screenshots, or source code.**

---

# 12. Local Development

Create the project environment using the dependency workflow defined by the repository.

Example Python virtual environment workflow:

```bash
python -m venv .venv
```

Activate the environment using the command appropriate for the operating system.

Then install the project's declared dependencies.

For development, the FastAPI development server may be used with auto-reload.

Do not use development auto-reload in production. FastAPI explicitly documents `--reload` as a development feature and warns against using it in production.

---

# 13. Running the Pipeline

SSIP consists of multiple processing stages.

The implementation should expose or document the authoritative commands for:

```text
1. Storefront ingestion
2. Bronze persistence
3. Bronze → Silver transformation
4. External enrichment
5. Gold generation
6. API serving
```

The README intentionally does not invent these commands because the supplied source documents the modules but does not establish their exact CLI interfaces.

Before deployment, the repository should expose one canonical documented execution path, for example:

```bash
# Ingestion
<actual-command>

# Silver transformation
<actual-command>

# Enrichment
<actual-command>

# Gold generation
<actual-command>
```

Replace the placeholders with the commands implemented by the repository.

---

# 14. Production API Startup

The production API must use a production ASGI server configuration.

For FastAPI, the current official guidance uses `fastapi run` for production rather than `fastapi dev`.

The exact SSIP entrypoint must match the repository implementation:

```text
app.main:app
```

if `app/main.py` exposes:

```python
app = FastAPI(...)
```

A representative production invocation is:

```bash
fastapi run app/main.py
```

or the repository's configured equivalent.

Do **not** use:

```bash
fastapi dev
```

for production.

If deployed behind a reverse proxy, HTTPS should be terminated at the appropriate infrastructure boundary. FastAPI's deployment documentation describes this as a standard production concern.

---

# 15. Container Deployment

If SSIP is containerized, the production image should contain:

```text
Application code
Production dependencies
Runtime configuration interface
ASGI server
```

A containerized deployment provides a reproducible environment and simplifies startup/restart behavior. FastAPI's deployment documentation specifically recommends containerization as a common production approach.

The repository should provide:

```text
Dockerfile
.dockerignore
```

and, if required:

```text
docker-compose.yml
```

or the deployment configuration appropriate to the selected infrastructure.

The container must not contain:

* API keys
* Shopify credentials
* webhook secrets
* private tokens
* developer-specific paths

---

# 16. Health Checks

Production SSIP should expose a lightweight health endpoint.

Recommended contract:

```text
GET /health
```

Example:

```json
{
  "status": "ok"
}
```

If the application requires external dependencies before it can serve traffic, a separate readiness endpoint is recommended:

```text
GET /ready
```

The distinction should be:

```text
/health
    Process is alive.

 /ready
    Application is capable of serving production traffic.
```

The exact endpoints must be implemented before deployment if they do not already exist.

---

# 17. Authentication

SSIP currently documents API-key authentication through:

```text
x-api-key
```

Keys must:

* be stored outside source control
* be compared using constant-time comparison
* be rotatable
* never appear in logs
* never appear in error responses
* never be embedded in frontend source code

Production frontend applications should not receive privileged server-side credentials.

For the eventual ADL API Demo, use a deliberately constrained public/demo access mechanism rather than exposing a production tenant API key.

---

# 18. Tenant Isolation

Tenant isolation is a production security boundary.

Every tenant-aware request must be evaluated against the authenticated tenant identity.

The system must not trust:

```text
merchant_id
store_url
store_id
```

from a client request without authorization validation.

The effective security model is:

```text
Authenticated API Key
        │
        ▼
Authorized Tenant
        │
        ▼
Authorized Store Domain
        │
        ▼
Tenant-Scoped Dataset
```

Any test that demonstrates cross-tenant access is a release blocker.

---

# 19. Data Provenance

SSIP distinguishes data according to provenance:

```text
OBSERVED
EXTERNAL
SIMULATED
```

This distinction must survive downstream transformations.

Consumers must be able to distinguish:

* direct storefront observations
* externally sourced intelligence
* calculated/simulated fallback values

This is important for data trust and downstream decision-making.

---

# 20. Storage & Persistence

SSIP uses:

```text
Bronze Lake
Silver Lake
Gold Lake
```

with Gold analytical datasets documented as Parquet-based data products.

Production deployment must ensure that these datasets are stored on persistent storage rather than ephemeral container filesystems.

The deployment documentation should explicitly define:

```text
Bronze storage location
Silver storage location
Gold storage location
Backup location
Retention policy
Recovery procedure
```

These values must be defined by the production infrastructure before deployment.

---

# 21. Scheduling & Pipeline Operations

A production SSIP installation requires an execution mechanism for recurring ingestion and enrichment.

The scheduler may be:

```text
Cron
Cloud Scheduler
CI/CD scheduler
Container scheduler
Workflow orchestrator
```

The selected mechanism must be documented in the deployment configuration.

The operational flow should remain:

```text
Schedule
   ↓
Ingestion
   ↓
Bronze
   ↓
Silver
   ↓
Enrichment
   ↓
Gold
   ↓
API consumers
```

The API should not depend on an interactive developer process to generate production data.

---

# 22. Testing

Before production deployment, the repository should provide a repeatable test command.

The production gate should cover at minimum:

### Unit tests

* normalization
* pricing calculations
* serving calculations
* enrichment logic
* validation

### Integration tests

* ingestion
* storage
* enrichment clients
* Gold generation

### API tests

* authentication
* authorization
* tenant isolation
* valid responses
* invalid requests
* error handling
* webhook signatures
* idempotency

### Smoke test

After deployment:

```text
Health endpoint
        ↓
Authenticated API request
        ↓
Known tenant
        ↓
Known dataset
        ↓
Expected response
```

---

# 23. Security Requirements

Production SSIP must enforce:

* HTTPS
* secure secret storage
* API-key protection
* constant-time credential comparison
* tenant isolation
* request validation
* webhook signature verification
* idempotency
* controlled CORS
* non-sensitive logging
* dependency pinning
* secure production configuration

Never deploy with:

```text
DEBUG=true
development credentials
hard-coded secrets
unrestricted CORS
development reload
```

---

# 24. Observability

Production operation should provide sufficient visibility to answer:

> What failed, when did it fail, which pipeline run was affected, and what data was produced?

Recommended operational fields include:

```text
run_id
crawl_id
merchant_id
store_url
crawl_timestamp
pipeline_stage
status
error_type
duration
record_count
```

Logs must not contain:

* API keys
* access tokens
* webhook secrets
* unnecessary personal data

Pipeline failures should be observable independently from API failures.

---

# 25. Error Handling

The API should return structured errors rather than leaking internal stack traces.

At minimum, consumers should be able to distinguish:

```text
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
429 Too Many Requests
500 Internal Server Error
503 Service Unavailable
```

Internal exception details belong in controlled server logs, not production API responses.

---

# 26. API Versioning

Production endpoints should be versioned.

Recommended structure:

```text
/api/v1/...
```

Versioning allows the ADL frontend and future API consumers to remain stable while SSIP evolves.

Breaking API changes should require a new API version rather than silently changing an existing contract.

---

# 27. Deployment Architecture

A production SSIP deployment should conceptually look like:

```text
                  ┌─────────────────────┐
                  │ Shopify / Web       │
                  │ External Signals    │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ SSIP Ingestion      │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ Bronze Lake         │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ Silver Lake         │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ Enrichment Engine   │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ Gold Lake           │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ FastAPI Serving API │
                  └──────────┬──────────┘
                             │
                   ┌─────────┴─────────┐
                   ▼                   ▼
             ADL Frontend         API Clients
```

The deployment infrastructure may change without changing this logical architecture.

---

# 28. Production Deployment Procedure

Use the following sequence.

## Step 1 — Validate the repository

Confirm:

```text
[ ] Dependency manifest exists
[ ] Lock/pinning strategy exists
[ ] Application entrypoint exists
[ ] Tests exist
[ ] Configuration is externalized
[ ] Secrets are absent from Git
[ ] Data directories are defined
```

## Step 2 — Configure production secrets

Configure all required environment variables using the deployment platform's secret-management mechanism.

Never commit production `.env` files.

## Step 3 — Build

Build the production artifact/container from the repository.

## Step 4 — Run tests

Run the complete test suite.

No production deployment should proceed if critical tests fail.

## Step 5 — Initialize persistent storage

Ensure Bronze, Silver, and Gold storage is available.

## Step 6 — Start the API

Start the FastAPI application using its production entrypoint.

## Step 7 — Verify health

```text
GET /health
```

## Step 8 — Verify authentication

Attempt:

```text
Unauthenticated request → rejected
Valid authenticated request → accepted
Invalid API key → rejected
```

## Step 9 — Verify tenant isolation

Attempt to access another tenant's data.

Expected result:

```text
Access denied
```

## Step 10 — Run a production smoke test

Verify:

```text
Ingestion
→ Bronze
→ Silver
→ Enrichment
→ Gold
→ API
```

## Step 11 — Verify monitoring

Confirm logs and operational monitoring are receiving production events.

## Step 12 — Release

Only after the complete smoke test passes should the API be considered production-ready.

---

# 29. Troubleshooting

## API does not start

Check:

```text
Python/runtime version
Dependency installation
Environment variables
Application import path
Port configuration
```

## Authentication fails

Check:

```text
x-api-key header
Configured API key
Secret formatting
Environment loading
```

## No data returned

Check:

```text
Merchant configuration
Bronze data
Silver transformation
Enrichment status
Gold dataset availability
Tenant authorization
```

## Webhook delivery fails

Check:

```text
Endpoint availability
HMAC signature
Retry status
Idempotency key
DLQ
```

## Data appears stale

Check:

```text
Scheduler
Pipeline execution
Latest crawl_timestamp
Pipeline run status
Gold regeneration
```

---

# 30. Production Deployment Checklist

Before declaring SSIP production-ready:

### Repository

* [ ] README synchronized with implementation
* [ ] Dependency manifest present
* [ ] Dependencies pinned/locked
* [ ] `.gitignore` configured
* [ ] `.env.example` present
* [ ] No secrets committed

### Application

* [ ] FastAPI production entrypoint verified
* [ ] Development reload disabled
* [ ] Production environment configured
* [ ] CORS restricted
* [ ] API versioning implemented
* [ ] Health endpoint implemented

### Security

* [ ] API authentication tested
* [ ] Constant-time API-key validation verified
* [ ] Tenant isolation tested
* [ ] Secrets stored securely
* [ ] HTTPS enabled
* [ ] Webhook signatures verified
* [ ] Idempotency tested

### Data

* [ ] Bronze persistence verified
* [ ] Silver transformation verified
* [ ] Gold datasets generated
* [ ] Provenance fields preserved
* [ ] Persistent storage configured
* [ ] Backup/recovery strategy defined

### Pipeline

* [ ] Ingestion tested
* [ ] Enrichment tested
* [ ] Gold generation tested
* [ ] Scheduling configured
* [ ] Failure handling verified

### API

* [ ] OpenAPI documentation verified
* [ ] Authentication documented
* [ ] Tenant behavior verified
* [ ] Error responses verified
* [ ] Response schemas verified
* [ ] API smoke test passed

### Operations

* [ ] Logging enabled
* [ ] Pipeline failures observable
* [ ] API failures observable
* [ ] Run IDs available
* [ ] DLQ operational
* [ ] Restart behavior verified

### Release

* [ ] Full test suite passes
* [ ] Production build succeeds
* [ ] Health check succeeds
* [ ] Authenticated request succeeds
* [ ] Unauthorized request fails
* [ ] Tenant isolation test passes
* [ ] End-to-end pipeline smoke test passes

---

# 31. Design Principles

### Merchant Decisions First

Every metric should answer an explicit commercial question.

### Domain Context Over Raw Data

A price change is not necessarily a commercial price change if servings, container size, bundles, or subscription terms also changed.

### Strict Data Provenance

Every intelligence signal should retain its origin:

```text
OBSERVED
EXTERNAL
SIMULATED
```

### Reliability & Data Quality

SSIP prioritizes:

* deterministic transformations
* deduplication
* normalization
* schema contracts
* provenance
* historical preservation

over unvalidated data volume.

### Separation of Concerns

The system maintains a clear separation between:

```text
Ingestion
    ↓
Normalization
    ↓
Enrichment
    ↓
Decision Data
    ↓
Serving
```

This allows individual layers to evolve without coupling the entire system.

---

# 32. Relationship to Ainga Data Labs

SSIP is a data intelligence subsystem within **Ainga Data Labs (ADL)**.

Its responsibility is to transform Shopify supplement-market observations into structured intelligence that can be consumed by:

```text
ADL internal systems
ADL API products
ADL frontend experiences
API clients
Commercial intelligence workflows
```

The SSIP backend should therefore be treated as an independently deployable data product and API service rather than as frontend infrastructure.

The ADL frontend should consume **stable, documented API contracts** rather than directly accessing Bronze, Silver, or Gold storage.

---

# 33. Production Boundary

The intended production boundary is:

```text
                 SSIP
┌───────────────────────────────────────┐
│                                       │
│  Ingestion                            │
│       ↓                               │
│  Bronze                               │
│       ↓                               │
│  Silver                               │
│       ↓                               │
│  Enrichment                           │
│       ↓                               │
│  Gold                                 │
│       ↓                               │
│  FastAPI Serving Layer                │
│                                       │
└──────────────────┬────────────────────┘
                   │
                   │ Versioned API
                   ▼
              ADL Frontend
```

The frontend is a consumer of SSIP.

It is not responsible for pipeline execution, raw-data storage, enrichment, or tenant-level data processing.

---

# 34. Current Status

SSIP contains the core architecture for:

* Shopify storefront ingestion
* Bronze persistence
* Silver normalization
* supplement-specific enrichment
* Gold commercial datasets
* multi-tenant FastAPI serving
* API-key authentication
* webhook processing
* provenance-aware intelligence

Production deployment is complete only after the operational requirements in this README have been implemented and verified against the actual repository.

---

## Maintainer

**Ainga Data Labs**

Shopify Supplements Intelligence Pipeline (SSIP)
