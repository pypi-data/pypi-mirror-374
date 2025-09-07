"""
NASDAQ Public API Client
========================

A Python client for accessing NASDAQ market data through their public API.

This package provides free access to NASDAQ data by refreshing cookies
from their public website using Selenium automation.
"""

from .core.cookie_manager import NASDAQCookieManager
from .nasdaq_data_ingestor import NASDAQDataIngestor


__all__ = ["NASDAQCookieManager", "NASDAQDataIngestor"]
__version__ = "1.0.0"
