"""
Main NASDAQ data ingestor combining all fetcher modules.
"""

import logging
from typing import Any

import pandas as pd

from .core.base_fetcher import NASDAQDataIngestorBase
from .core.cookie_manager import NASDAQCookieManager
from .fetchers.financial import FinancialDataFetcher
from .fetchers.market import MarketDataFetcher
from .fetchers.ownership import OwnershipDataFetcher
from .fetchers.regulatory import RegulatoryDataFetcher


logger = logging.getLogger(__name__)


class NASDAQDataIngestor(NASDAQDataIngestorBase):
    """Enhanced NASDAQ data ingestion with comprehensive data fetching capabilities."""

    def __init__(self, cookie_manager: NASDAQCookieManager | None = None):
        """
        Initialize NASDAQ data ingestor.

        Args:
            cookie_manager: Optional cookie manager instance
        """
        super().__init__(cookie_manager)
        self.cookie_manager = cookie_manager or NASDAQCookieManager()

        # Initialize all fetcher modules
        self._financial_fetcher = FinancialDataFetcher(cookie_manager)
        self._market_fetcher = MarketDataFetcher(cookie_manager)
        self._ownership_fetcher = OwnershipDataFetcher(cookie_manager)
        self._regulatory_fetcher = RegulatoryDataFetcher(cookie_manager)

    # Financial data methods
    def fetch_company_profile(self, symbol: str) -> str:
        """Fetch company description from NASDAQ API."""
        return self._financial_fetcher.fetch_company_profile(symbol)

    def fetch_revenue_earnings(self, symbol: str) -> list[dict[str, Any]]:
        """Fetch revenue and earnings data for the given stock symbol."""
        return self._financial_fetcher.fetch_revenue_earnings(symbol)

    def fetch_historical_quotes(
        self, symbol: str, period: int = 5, asset_class: str = "stock"
    ) -> dict[str, dict[str, Any]]:
        """Fetch historical prices for the given stock symbol."""
        return self._financial_fetcher.fetch_historical_quotes(symbol, period, asset_class)

    def fetch_dividend_history(self, symbol: str) -> list[dict[str, Any]]:
        """Fetch dividend history data for the given stock symbol."""
        return self._financial_fetcher.fetch_dividend_history(symbol)

    def fetch_financial_ratios(self, symbol: str) -> dict[str, Any]:
        """Fetch financial ratios data for the given stock symbol."""
        return self._financial_fetcher.fetch_financial_ratios(symbol)

    def fetch_option_chain(self, symbol: str, money_type: str = "ALL") -> dict[str, Any]:
        """Fetch option chain data for the given stock symbol."""
        return self._financial_fetcher.fetch_option_chain(symbol, money_type)

    # Market data methods
    def fetch_earnings_calendar(self, days_ahead: int = 7) -> pd.DataFrame:
        """Fetch earnings calendar for upcoming days."""
        return self._market_fetcher.fetch_earnings_calendar(days_ahead)

    def fetch_nasdaq_screener_data(self) -> pd.DataFrame:
        """Fetch both NASDAQ stock and ETF data and combine them."""
        return self._market_fetcher.fetch_nasdaq_screener_data()

    def fetch_stock_news(self, symbol: str, days_back: int = 7) -> list[dict[str, str]]:
        """Fetch recent stock news for the given symbol."""
        return self._market_fetcher.fetch_stock_news(symbol, days_back)

    def fetch_press_releases(self, symbol: str, days_back: int = 15) -> list[dict[str, str]]:
        """Fetch recent press releases for the given symbol."""
        return self._market_fetcher.fetch_press_releases(symbol, days_back)

    # Ownership data methods
    def fetch_insider_trading(self, symbol: str) -> dict[str, Any]:
        """Fetch insider trading data for the given stock symbol."""
        return self._ownership_fetcher.fetch_insider_trading(symbol)

    def fetch_institutional_holdings(self, symbol: str) -> dict[str, Any]:
        """Fetch institutional holdings data for the given stock symbol."""
        return self._ownership_fetcher.fetch_institutional_holdings(symbol)

    def fetch_short_interest(self, symbol: str) -> list[dict[str, Any]]:
        """Fetch short interest data for the given stock symbol."""
        return self._ownership_fetcher.fetch_short_interest(symbol)

    # Regulatory data methods
    def fetch_sec_filings(self, symbol: str, filing_type: str = "ALL") -> list[dict[str, Any]]:
        """Fetch SEC filings data for the given stock symbol."""
        return self._regulatory_fetcher.fetch_sec_filings(symbol, filing_type)
