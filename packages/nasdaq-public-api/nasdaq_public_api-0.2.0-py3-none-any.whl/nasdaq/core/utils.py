"""
Utility functions for NASDAQ data processing.
"""

import logging
from datetime import datetime

import requests

from ..config.settings import _nasdaq_headers
from ..core.cookie_manager import refresh_nasdaq_cookie


logger = logging.getLogger(__name__)


def safe_get_nested(data: dict, *keys: str, default="default"):
    """
    Safely access nested dictionary values without raising AttributeError.

    Args:
        data: The dictionary to traverse
        *keys: The keys to access in order
        default: Default value if path doesn't exist

    Returns:
        The value at the nested location or default if not found
    """
    try:
        for key in keys:
            if not isinstance(data, dict):
                return default
            data = data.get(key, default)
        return data
    except AttributeError:
        return default


def safe_parse_date(date_str: str, fmt: str) -> datetime | None:
    """Safely parse date string with error handling."""
    try:
        return datetime.strptime(date_str, fmt)
    except Exception as e:
        logger.error(f"Error parsing date '{date_str}': {e}")
        return None


def get_full_url(url: str) -> str:
    """Convert relative URLs to full NASDAQ URLs."""
    return "https://www.nasdaq.com" + url if url.startswith("/") else url


def fetch_nasdaq_api(url: str) -> dict:
    """
    Fetch data from the Nasdaq API using the provided URL.

    Args:
        url: The API endpoint URL

    Returns:
        dict: JSON response from the API

    Raises:
        requests.RequestException: If the API request fails
    """
    # Refresh cookies if needed
    refresh_nasdaq_cookie()

    response = requests.get(url, headers=_nasdaq_headers.copy())
    response.raise_for_status()
    return response.json()
