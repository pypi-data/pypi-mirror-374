"""
Ownership and insider trading data fetchers for NASDAQ.
"""

import logging
from typing import Any

from ..core.base_fetcher import NASDAQDataIngestorBase
from ..core.utils import fetch_nasdaq_api
from ..core.utils import safe_get_nested


logger = logging.getLogger(__name__)


class OwnershipDataFetcher(NASDAQDataIngestorBase):
    """Ownership and insider trading data fetchers for NASDAQ."""

    def fetch_insider_trading(self, symbol: str) -> dict[str, Any]:
        """
        Fetch insider trading data for the given stock symbol.

        Args:
            symbol: Stock symbol

        Returns:
            Dict: Insider trading information
        """
        try:
            insider_trading_url = (
                f"https://api.nasdaq.com/api/company/{symbol}/insider-trades?"
                f"limit=10&type=all&sortColumn=lastDate&sortOrder=DESC"
            )
            json_data = fetch_nasdaq_api(insider_trading_url)
            data = json_data.get("data", {})
            if data is None:
                return {}

            # Extract relevant information
            number_of_trades = data.get("numberOfTrades", {}).get("rows", [])
            number_of_shares_traded = data.get("numberOfSharesTraded", {}).get("rows", [])
            transaction_table = data.get("transactionTable", {}).get("table", {}).get("rows") or []

            # Remove the "url" field from each transaction
            cleaned_transaction_table = [self._clean_data_dict(item) for item in transaction_table]

            return {
                "number_of_trades": number_of_trades,
                "number_of_shares_traded": number_of_shares_traded,
                "transaction_table": cleaned_transaction_table,
            }

        except Exception as e:
            logger.error(f"Error fetching insider trading for {symbol}: {e}")
            return {}

    def fetch_institutional_holdings(self, symbol: str) -> dict[str, Any]:
        """
        Fetch institutional holdings data for the given stock symbol.

        Args:
            symbol: Stock symbol

        Returns:
            Dict: Institutional holdings information
        """
        try:
            institutional_holdings_url = (
                f"https://api.nasdaq.com/api/company/{symbol}/institutional-holdings?"
                f"limit=10&type=TOTAL&sortColumn=marketValue"
            )
            json_data = fetch_nasdaq_api(institutional_holdings_url)
            data = json_data.get("data", {})

            if not data:
                logger.warning(f"No institutional holdings data for {symbol}")
                return {}

            # Extract relevant information using safe nested access
            ownership_summary = safe_get_nested(data, "ownershipSummary", default={})
            active_positions = safe_get_nested(data, "activePositions", "rows", default=[])
            new_sold_out_positions = safe_get_nested(data, "newSoldOutPositions", "rows", default=[])
            holdings_transactions = safe_get_nested(data, "holdingsTransactions", "table", "rows", default=[])

            # Clean holdings transactions by removing URL field
            cleaned_holdings_transactions = [self._clean_data_dict(item) for item in holdings_transactions]

            return {
                "ownership_summary": ownership_summary,
                "active_positions": active_positions,
                "new_sold_out_positions": new_sold_out_positions,
                "holdings_transactions": cleaned_holdings_transactions,
            }

        except Exception as e:
            logger.error(f"Error fetching institutional holdings for {symbol}: {e}")
            return {}

    def fetch_short_interest(self, symbol: str) -> list[dict[str, Any]]:
        """
        Fetch short interest data for the given stock symbol.

        Args:
            symbol: Stock symbol

        Returns:
            List[Dict]: Short interest data (last 4 entries)
        """
        try:
            short_interest_url = f"https://api.nasdaq.com/api/quote/{symbol}/short-interest?assetClass=stocks"
            json_data = fetch_nasdaq_api(short_interest_url)
            data = json_data.get("data", {})
            if data is None:
                return []

            short_interest_table = data.get("shortInterestTable") or {}
            rows = short_interest_table.get("rows") or []

            # Return only the 4 most recent rows
            return rows[:4]

        except Exception as e:
            logger.error(f"Error fetching short interest for {symbol}: {e}")
            return []
