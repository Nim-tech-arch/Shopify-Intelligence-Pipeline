"""Compatibility package for the renamed Shopify-Supplements module.

This package exists so old imports like `from shopify.analytics import ...`
continue to work while the real source files live in `Shopify-Supplements`.
"""

import os

__path__.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Shopify-Supplements")))
