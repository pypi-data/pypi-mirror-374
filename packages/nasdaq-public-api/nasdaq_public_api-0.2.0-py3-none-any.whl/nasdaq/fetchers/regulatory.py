"""
Regulatory and SEC filings data fetchers for NASDAQ.
"""

import logging
from typing import Any

from ..core.base_fetcher import NASDAQDataIngestorBase
from ..core.utils import fetch_nasdaq_api


logger = logging.getLogger(__name__)


class RegulatoryDataFetcher(NASDAQDataIngestorBase):
    """Regulatory and SEC filings data fetchers for NASDAQ."""

    def fetch_sec_filings(self, symbol: str, filing_type: str = "ALL") -> list[dict[str, Any]]:
        """
        Fetch SEC filings data for the given stock symbol.

        Args:
            symbol: Stock symbol
            filing_type: Type of filings to fetch (ALL, 10-K, 10-Q, 8-K, etc.)

        Returns:
            List[Dict]: SEC filings data
        """
        try:
            # Updated API endpoint with correct parameters
            sec_filings_url = (
                f"https://api.nasdaq.com/api/company/{symbol}/sec-filings?limit=10&filingType={filing_type}"
            )
            json_data = fetch_nasdaq_api(sec_filings_url)
            data = json_data.get("data", {})
            if data is None:
                return []

            # Extract filings table - check for the new structure first
            if "rows" in data:
                # New structure - rows are directly in data
                rows = data.get("rows", [])
            else:
                # Old structure - rows are in filingsTable
                filings_table = data.get("filingsTable") or {}
                rows = filings_table.get("rows") or []

            # Clean up the data by removing any URL fields that might not be needed
            cleaned_rows = []
            for row in rows:
                # If view is a dict, we might want to extract specific links from it
                if "view" in row and isinstance(row["view"], dict) and "htmlLink" in row["view"]:
                    # Extract the main HTML link as the primary URL
                    row["url"] = row["view"]["htmlLink"]
                cleaned_rows.append(self._clean_data_dict(row, ["view"]))

            return cleaned_rows

        except Exception as e:
            logger.warning(f"SEC filings may not be available for {symbol}: {e}")
            return []
