"""
Base fetcher classes for NASDAQ data ingestion.
"""

from abc import ABC
from abc import abstractmethod
from typing import Any

# Import here to avoid circular imports
from .utils import safe_get_nested


class BaseNASDAQFetcher(ABC):
    """Base class for NASDAQ data fetchers with common functionality."""

    @abstractmethod
    def _safe_get_data(self, json_data: dict, *keys: str) -> Any:
        """
        Safely extract data from JSON response.

        Args:
            json_data: JSON response data
            *keys: Path to nested data

        Returns:
            Extracted data or None if not found
        """
        pass

    @abstractmethod
    def _safe_extract_rows(self, data: dict, table_key: str = "rows") -> list[dict]:
        """
        Safely extract rows from table data.

        Args:
            data: Data containing table structure
            table_key: Key for rows in table (default: "rows")

        Returns:
            List of rows or empty list if not found
        """
        pass

    @abstractmethod
    def _safe_convert_value(self, value: Any, conversion_type: str = "string") -> Any:
        """
        Safely convert values with error handling.

        Args:
            value: Value to convert
            conversion_type: Type to convert to ("string", "float", "int")

        Returns:
            Converted value or None if conversion fails
        """
        pass

    @abstractmethod
    def _clean_data_dict(self, data_dict: dict, exclude_keys: list[str] | None = None) -> dict:
        """
        Remove specified keys from data dictionary.

        Args:
            data_dict: Dictionary to clean
            exclude_keys: Keys to remove

        Returns:
            Cleaned dictionary
        """
        pass


class NASDAQDataIngestorBase(BaseNASDAQFetcher):
    """Base class for NASDAQ data ingestor with shared functionality."""

    def __init__(self, cookie_manager=None):
        """
        Initialize NASDAQ data ingestor base.

        Args:
            cookie_manager: Optional cookie manager instance
        """
        self.cookie_manager = cookie_manager

    def _safe_get_data(self, json_data: dict, *keys: str) -> Any:
        """
        Safely extract data from JSON response.

        Args:
            json_data: JSON response data
            *keys: Path to nested data

        Returns:
            Extracted data or None if not found
        """
        data = json_data.get("data", {})
        if not data:
            return None
        return safe_get_nested(data, *keys)

    def _safe_extract_rows(self, data: dict, table_key: str = "rows") -> list[dict]:
        """
        Safely extract rows from table data.

        Args:
            data: Data containing table structure
            table_key: Key for rows in table (default: "rows")

        Returns:
            List of rows or empty list if not found
        """
        if not data:
            return []

        if table_key in data:
            return data.get(table_key, [])

        # Try common table structures
        table = data.get("table", {})
        if table and isinstance(table, dict):
            return table.get(table_key, [])

        return []

    def _safe_convert_value(self, value: Any, conversion_type: str = "string") -> Any:
        """
        Safely convert values with error handling.

        Args:
            value: Value to convert
            conversion_type: Type to convert to ("string", "float", "int")

        Returns:
            Converted value or None if conversion fails
        """
        if not value or value == "N/A":
            return None

        try:
            if conversion_type == "float":
                # Handle currency and comma-separated values
                if isinstance(value, str):
                    value = value.replace("$", "").replace(",", "").replace("%", "")
                return float(value)
            elif conversion_type == "int":
                # Handle comma-separated values
                if isinstance(value, str):
                    value = value.replace(",", "")
                return int(value)
            else:
                return str(value)
        except (ValueError, TypeError, AttributeError):
            return None

    def _clean_data_dict(self, data_dict: dict, exclude_keys: list[str] | None = None) -> dict:
        """
        Remove specified keys from data dictionary.

        Args:
            data_dict: Dictionary to clean
            exclude_keys: Keys to remove

        Returns:
            Cleaned dictionary
        """
        if exclude_keys is None:
            exclude_keys = ["url"]

        return {k: v for k, v in data_dict.items() if k not in exclude_keys}
