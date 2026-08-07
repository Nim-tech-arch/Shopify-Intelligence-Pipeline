# E-commerce-Intelligence-Pipeline/shopify/config.py

TARGET_STORES = [
    "https://www.transparentlabs.com",
    "https://kaged.com",
    "https://ghostlifestyle.com",
    "https://www.cellucor.com",
]

STOREFRONT_TOKENS = {
    "https://www.transparentlabs.com": "",
    "https://kaged.com": "",
    "https://ghostlifestyle.com": "",
    "https://www.cellucor.com": "",
}

# Alias maps for cross-module compatibility
TARGET_SEEDS = TARGET_STORES

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
}

DEFAULT_HEADERS = HEADERS

REQUEST_TIMEOUT = 12.0
MAX_CONCURRENCY = 2

RATE_LIMIT_SETTINGS = {
    "min_jitter": 1.5,
    "max_jitter": 3.5,
    "max_concurrency": MAX_CONCURRENCY
}