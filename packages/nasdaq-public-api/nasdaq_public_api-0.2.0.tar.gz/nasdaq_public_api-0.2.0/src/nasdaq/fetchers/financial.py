"""
Financial data fetchers for NASDAQ.
"""

import logging
from datetime import datetime
from datetime import timedelta
from typing import Any

from ..core.base_fetcher import NASDAQDataIngestorBase
from ..core.utils import fetch_nasdaq_api


logger = logging.getLogger(__name__)


class FinancialDataFetcher(NASDAQDataIngestorBase):
    """Financial data fetchers for NASDAQ."""

    def fetch_company_profile(self, symbol: str) -> str:
        """
        Fetch company description from NASDAQ API.

        Args:
            symbol: Stock symbol

        Returns:
            str: Company description
        """
        try:
            profile_url = f"https://api.nasdaq.com/api/company/{symbol}/company-profile"
            json_data = fetch_nasdaq_api(profile_url)
            data = json_data.get("data", {})
            if data is None:
                return ""
            return data.get("CompanyDescription", {}).get("value", "")
        except Exception as e:
            logger.error(f"Error fetching company profile for {symbol}: {e}")
            return ""

    def fetch_revenue_earnings(self, symbol: str) -> list[dict[str, Any]]:
        """
        Fetch revenue and earnings data for the given stock symbol.

        Args:
            symbol: Stock symbol

        Returns:
            List[Dict]: Revenue and earnings data for last 6 quarters
        """
        try:
            revenue_earnings_url = f"https://api.nasdaq.com/api/company/{symbol}/revenue?limit=1"
            json_data = fetch_nasdaq_api(revenue_earnings_url)
            data = json_data.get("data")
            if not data:
                logger.warning(f"No revenue data found for {symbol}")
                return []

            revenue_table = data.get("revenueTable") or {}
            rows = revenue_table.get("rows") or []

            if not rows:
                logger.warning(f"No rows found in revenue table for {symbol}")
                return []

            # Transpose the table to only include groups containing 4 entries each
            transposed_data = []
            try:
                for i in range(0, len(rows), 4):
                    quarter_data = {
                        "quarter": rows[i]["value1"],
                        "revenue": self._safe_convert_value(rows[i + 1]["value2"]),
                        "eps": self._safe_convert_value(rows[i + 2]["value2"]),
                        "dividends": self._safe_convert_value(rows[i + 3]["value2"]),
                    }
                    transposed_data.append(quarter_data)
            except Exception as e:
                logger.error(f"Error processing revenue rows for {symbol}: {e}")
                return []

            # Keep only the last 6 quarters
            return transposed_data[-6:]

        except Exception as e:
            logger.error(f"Error fetching revenue/earnings for {symbol}: {e}")
            return []

    def fetch_historical_quotes(
        self, symbol: str, period: int = 5, asset_class: str = "stock"
    ) -> dict[str, dict[str, Any]]:
        """
        Fetch historical prices for the given stock symbol.

        Args:
            symbol: Stock symbol
            period: Number of days of historical data
            asset_class: "stock" or "etf"

        Returns:
            Dict: Historical price data with dates as keys
        """
        try:
            # Calculate dates for the API request
            end_date = datetime.now()
            calendar_days_threshold = 150
            calendar_days = period * 1.5 if period >= calendar_days_threshold else period
            start_date = end_date - timedelta(days=int(calendar_days))
            asset_class = "stocks" if asset_class == "stock" else "etf"

            historical_url = (
                f"https://api.nasdaq.com/api/quote/{symbol}/historical?"
                f"assetclass={asset_class}&fromdate={start_date.strftime('%Y-%m-%d')}&"
                f"limit={int(calendar_days)}&todate={end_date.strftime('%Y-%m-%d')}"
            )

            json_data = fetch_nasdaq_api(historical_url)
            data = json_data.get("data", {})
            if data is None:
                return {}

            # Extract the trades table
            trades_data = data.get("tradesTable", {}).get("rows") or []

            prices_dict = {}
            for row in trades_data:
                prices_dict[row["date"]] = {
                    "close": self._safe_convert_value(row.get("close"), "float"),
                    "volume": self._safe_convert_value(row.get("volume"), "int"),
                    "open": self._safe_convert_value(row.get("open"), "float"),
                    "high": self._safe_convert_value(row.get("high"), "float"),
                    "low": self._safe_convert_value(row.get("low"), "float"),
                }

            return prices_dict

        except Exception as e:
            logger.error(f"Error fetching historical quotes for {symbol}: {e}")
            return {}

    def fetch_dividend_history(self, symbol: str) -> list[dict[str, Any]]:
        """
        Fetch dividend history data for the given stock symbol.

        Args:
            symbol: Stock symbol

        Returns:
            List[Dict]: Dividend history data
        """
        try:
            dividend_url = f"https://api.nasdaq.com/api/quote/{symbol}/dividends?assetClass=stocks"
            json_data = fetch_nasdaq_api(dividend_url)
            data = json_data.get("data", {})
            if data is None:
                return []

            # Check for the new API structure first
            if "dividends" in data and "rows" in data["dividends"]:
                rows = data["dividends"]["rows"]
            else:
                # Fallback to old structure
                dividend_table = data.get("dividendTable") or {}
                rows = dividend_table.get("rows") or []

            return rows

        except Exception as e:
            logger.warning(f"Dividend history may not be available for {symbol}: {e}")
            return []

    def _fetch_ratios_from_quote_endpoint(self, symbol: str) -> dict[str, Any]:
        """Fetch ratios from the quote-based endpoint."""
        try:
            ratios_url = f"https://api.nasdaq.com/api/quote/{symbol}/ratios?assetClass=stocks"
            json_data = fetch_nasdaq_api(ratios_url)
            return json_data.get("data", {})
        except Exception as e:
            logger.debug(f"Quote-based ratios not available for {symbol}: {e}")
            return {}

    def _fetch_ratios_from_company_endpoint(self, symbol: str) -> dict[str, Any]:
        """Fetch ratios from the company-based endpoint."""
        try:
            ratios_url = f"https://api.nasdaq.com/api/company/{symbol}/ratios"
            json_data = fetch_nasdaq_api(ratios_url)
            return json_data.get("data", {})
        except Exception as e:
            logger.debug(f"Company-based ratios not available for {symbol}: {e}")
            return {}

    def _fetch_ratios_from_key_stats(self, symbol: str) -> dict[str, Any]:
        """Fetch basic financial info from key stats as fallback."""
        try:
            key_stats_url = f"https://api.nasdaq.com/api/quote/{symbol}/info?assetclass=stocks"
            json_data = fetch_nasdaq_api(key_stats_url)
            return json_data.get("data", {})
        except Exception as e:
            logger.debug(f"Key stats not available for {symbol}: {e}")
            return {}

    def _process_ratio_table_data(self, data: dict) -> dict[str, Any]:
        """Process ratio table data from the original approach."""
        ratios_dict = {}
        if "ratioTable" in data and data.get("ratioTable"):
            ratios_data = data.get("ratioTable") or {}
            rows = ratios_data.get("rows") or []
            for row in rows:
                ratio_name = row.get("name", "")
                if ratio_name:
                    ratios_dict[ratio_name] = {
                        "value": row.get("value", ""),
                        "displayValue": row.get("displayValue", ""),
                    }
        return ratios_dict

    def _process_key_stats_data(self, data: dict) -> dict[str, Any]:
        """Process key stats data for basic financial metrics."""
        ratios_dict = {}
        if "keyStats" in data and data.get("keyStats"):
            key_stats = data.get("keyStats", {})
            # Extract 52 week high/low as basic financial info
            if "fiftyTwoWeekHighLow" in key_stats:
                fifty_two_week = key_stats["fiftyTwoWeekHighLow"]
                ratios_dict["52 Week Range"] = {
                    "value": fifty_two_week.get("value", ""),
                    "displayValue": fifty_two_week.get("value", ""),
                }
            if "dayrange" in key_stats:
                day_range = key_stats["dayrange"]
                ratios_dict["Day Range"] = {
                    "value": day_range.get("value", ""),
                    "displayValue": day_range.get("value", ""),
                }
        return ratios_dict

    def _process_primary_data(self, data: dict) -> dict[str, Any]:
        """Process primary data for basic stock information."""
        ratios_dict = {}
        if "primaryData" in data and data.get("primaryData"):
            primary_data = data["primaryData"]
            if "lastSalePrice" in primary_data:
                ratios_dict["Current Price"] = {
                    "value": primary_data["lastSalePrice"].replace("$", ""),
                    "displayValue": primary_data["lastSalePrice"],
                }
            if "percentageChange" in primary_data:
                ratios_dict["Percent Change"] = {
                    "value": primary_data["percentageChange"].replace("%", ""),
                    "displayValue": primary_data["percentageChange"],
                }
        return ratios_dict

    def fetch_financial_ratios(self, symbol: str) -> dict[str, Any]:
        """
        Fetch financial ratios data for the given stock symbol.

        Args:
            symbol: Stock symbol

        Returns:
            Dict: Financial ratios data
        """
        # Try different endpoints in order of preference
        data = self._fetch_ratios_from_quote_endpoint(symbol)
        if not data:
            data = self._fetch_ratios_from_company_endpoint(symbol)
        if not data:
            data = self._fetch_ratios_from_key_stats(symbol)

        if not data:
            return {}

        # Extract relevant ratio information based on what's available
        ratios_dict = self._process_ratio_table_data(data)
        if not ratios_dict:
            # If no ratioTable, try to extract basic financial metrics from key stats
            ratios_dict.update(self._process_key_stats_data(data))

        # Also extract some basic stock info that might be useful
        ratios_dict.update(self._process_primary_data(data))

        return ratios_dict

    def fetch_option_chain(self, symbol: str, money_type: str = "ALL") -> dict[str, Any]:
        """
        Fetch option chain data for the given stock symbol.

        Args:
            symbol: Stock symbol
            money_type: Type of options to fetch (ALL, ITM, OTM, etc.)

        Returns:
            Dict: Option chain data
        """
        try:
            # First try the quote-based option chain endpoint
            option_chain_url = (
                f"https://api.nasdaq.com/api/quote/{symbol}/option-chain?"
                f"assetClass=stocks&moneyType={money_type}&expiryType=ALL"
            )
            json_data = fetch_nasdaq_api(option_chain_url)
            data = json_data.get("data", {})

            # If that doesn't work, return empty dict
            if data is None:
                return {}

            return data

        except Exception as e:
            logger.warning(f"Option chain may not be available for {symbol}: {e}")
            return {}
