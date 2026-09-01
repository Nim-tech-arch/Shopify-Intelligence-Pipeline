"""Configuration module for the Shopify Intelligence Pipeline.

Loads runtime parameters from environment variables with sensible defaults
and provides canonicalized target store definitions.
"""

import os
from typing import Dict, List, Optional
from urllib.parse import urlparse

from pydantic import HttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def normalize_store_url(url: str) -> str:
    """Canonicalizes target storefront URLs by enforcing HTTPS, stripping

    trailing slashes, and lowercasing.
    """
    parsed = urlparse(url.strip())
    scheme = parsed.scheme if parsed.scheme else "https"
    netloc = parsed.netloc if parsed.netloc else parsed.path
    # Strip trailing slashes and normalize path
    clean_url = f"{scheme}://{netloc}".rstrip("/").lower()
    return clean_url


DEFAULT_TARGET_STORES: List[str] = [
    # Original core supplement competitor set
    "https://www.transparentlabs.com",
    "https://kaged.com",
    "https://ghostlifestyle.com",
    "https://www.cellucor.com",
    "https://legionathletics.com",
    "https://nootropicsdepot.com",
    "https://gorillamind.com",
    "https://pescience.com",
    # Sports nutrition / supplements / wellness expansion set
    "https://nutricost.com",
    "https://www.naturemade.com",
    "https://nakednutrition.com",
    "https://www.olly.com",
    "https://www.bulksupplements.com",
    "https://beekeepersnaturals.com",
    "https://www.codeage.com",
    "https://www.livemomentous.com",
    "https://appliednutrition.uk",
    "https://5percentnutrition.com",
    "https://bpisports.com",
    "https://bloomnu.com",
    "https://ancestralsupplements.com",
    "https://apothekary.co",
    "https://shopbeam.com",
    "https://www.bubsnaturals.com",
    "https://greatlakeswellness.com",
    "https://wishgardenherbs.com",
    "https://dripdrop.com",
    "https://www.ultimareplenisher.com",
    "https://londonnootropics.com",
    "https://globalhealing.com",
    "https://www.wildnutrition.com",
    "https://mudwtr.com",
    "https://nutraorganics.com.au",
    "https://jarrow.com",
    "https://manukora.com",
    "https://proteanutrition.com",
    "https://nomadsupplements.store",
    "https://pinnaclesup.com",
    "https://asgardiannutrition.com",
    "https://ahlo.co.uk",
    "https://wassen.com",
    "https://prorganiqnutrition.com",
    "https://tru2u.health",
    "https://cloverhealth.shop",
    "https://wellnessgardensupplements.myshopify.com",
    "https://starsamnaturals.com",
    # Vitamins / supplements / wellness Shopify Plus DTC set
    "https://www.vitalproteins.com",
    "https://ritual.com",
    "https://goli.com",
    "https://www.alaninu.com",
    "https://doublewoodsupplements.com",
    "https://moonjuice.com",
    "https://maryruthorganics.com",
    "https://1upnutrition.com",
    "https://rysesupps.com",
    "https://bpnsupps.com",
    "https://www.promixnutrition.com",
    "https://steelsupplements.com",
    "https://www.ora-organic.com",
]


class PipelineSettings(BaseSettings):
    """Pipeline Settings bound to environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Ingestion Controls
    request_timeout: float = 12.0
    max_concurrency: int = 2
    min_jitter: float = 1.5
    max_jitter: float = 3.5

    # Target Store Sets
    raw_target_stores: List[str] = DEFAULT_TARGET_STORES

    # Base Request Headers
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )

    @property
    def target_stores(self) -> List[str]:
        """Returns normalized target store URLs."""
        return [normalize_store_url(url) for url in self.raw_target_stores]

    @property
    def default_headers(self) -> Dict[str, str]:
        return {
            "User-Agent": self.user_agent,
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.9",
            "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
        }


# Instantiate global settings object
settings = PipelineSettings()

# Exports for legacy non-breaking import compatibility
TARGET_STORES = settings.target_stores
TARGET_SEEDS = TARGET_STORES
STOREFRONT_TOKENS = {store: "" for store in TARGET_STORES}
HEADERS = settings.default_headers
DEFAULT_HEADERS = HEADERS
REQUEST_TIMEOUT = settings.request_timeout
MAX_CONCURRENCY = settings.max_concurrency
RATE_LIMIT_SETTINGS = {
    "min_jitter": settings.min_jitter,
    "max_jitter": settings.max_jitter,
    "max_concurrency": settings.max_concurrency,
    "timeout_seconds": settings.request_timeout,
}