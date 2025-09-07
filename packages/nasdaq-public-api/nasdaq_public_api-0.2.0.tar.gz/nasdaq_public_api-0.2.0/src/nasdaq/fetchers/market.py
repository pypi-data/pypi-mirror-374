"""
Market data and screener fetchers for NASDAQ.
"""

import logging
from datetime import datetime
from datetime import timedelta

import pandas as pd

from ..core.base_fetcher import NASDAQDataIngestorBase
from ..core.utils import fetch_nasdaq_api
from ..core.utils import get_full_url
from ..core.utils import safe_parse_date
from ..data_processing import TimeSeriesProcessor


logger = logging.getLogger(__name__)


class MarketDataFetcher(NASDAQDataIngestorBase):
    """Market data and screener fetchers for NASDAQ."""

    def fetch_earnings_calendar(self, days_ahead: int = 7) -> pd.DataFrame:
        """
        Fetch earnings calendar for upcoming days.

        Args:
            days_ahead: Number of days to look ahead

        Returns:
            DataFrame: Earnings calendar data
        """
        try:
            all_rows = []

            # Use pandas for date range generation
            date_range = TimeSeriesProcessor.create_earnings_calendar_dates(datetime.now(), days_ahead)

            for current_date in date_range:
                date_str = current_date.strftime("%Y-%m-%d")
                earnings_url = f"https://api.nasdaq.com/api/calendar/earnings?date={date_str}"

                try:
                    json_data = fetch_nasdaq_api(earnings_url)
                except Exception as e:
                    logger.error(f"Error fetching earnings for {date_str}: {e}")
                    continue

                data = json_data.get("data", {})
                if not data:
                    continue

                rows = data.get("rows") or []
                # Add the queried date to each row
                for row in rows:
                    row["callDate"] = date_str
                all_rows.extend(rows)

            df = pd.DataFrame(all_rows)

            if df.empty:
                return df

            try:
                # Use pandas for datetime operations
                df["earnings_date"] = pd.to_datetime(df["callDate"])
                df["days_to_earnings"] = (df["earnings_date"] - pd.Timestamp.now()).dt.days

                # Create the human-readable next_earning_call string
                mapping = [
                    ("callDate", "callDate"),
                    ("lastYearRptDt", "lastYearReportDate"),
                    ("lastYearEPS", "lastYearEPS"),
                    ("time", "reportTime"),
                    ("fiscalQuarterEnding", "fiscalQuarterEnding"),
                    ("epsForecast", "epsForecast"),
                    ("noOfEsts", "numberOfEstimates"),
                ]
                df["next_earning_call"] = df.apply(
                    lambda row: ", ".join(
                        f"{new_key}: {row[old_key]}"
                        for old_key, new_key in mapping
                        if old_key in row and pd.notnull(row[old_key])
                    ),
                    axis=1,
                )

                # Return only the necessary columns
                return df[["symbol", "next_earning_call", "days_to_earnings"]]

            except Exception as e:
                logger.error(f"Error processing earnings data: {e}")
                # In case of errors, still try to return minimal data
                if "callDate" in df.columns and "symbol" in df.columns:
                    df["next_earning_call"] = df.apply(lambda row: f"callDate: {row['callDate']}", axis=1)
                    df["days_to_earnings"] = None
                    return df[["symbol", "next_earning_call", "days_to_earnings"]]
                return pd.DataFrame(columns=["symbol", "next_earning_call", "days_to_earnings"])

        except Exception as e:
            logger.error(f"Error fetching earnings calendar: {e}")
            return pd.DataFrame(columns=["symbol", "next_earning_call", "days_to_earnings"])

    def fetch_nasdaq_screener_data(self) -> pd.DataFrame:
        """
        Fetch both NASDAQ stock and ETF data and combine them.

        Returns:
            DataFrame: Combined stock and ETF data
        """
        try:
            # Fetch stocks data
            stocks_api = "https://api.nasdaq.com/api/screener/stocks?tableonly=false&download=true"
            stocks_json_data = fetch_nasdaq_api(stocks_api)
            stocks_rows = stocks_json_data.get("data", {}).get("rows", [])
            stocks_df = pd.DataFrame(stocks_rows)

            if not stocks_df.empty:
                stocks_df["asset_type"] = "stock"

            # Fetch ETFs data
            etfs_api = "https://api.nasdaq.com/api/screener/etf?tableonly=false&download=true"
            etfs_json_data = fetch_nasdaq_api(etfs_api)
            etfs_rows = etfs_json_data.get("data", {}).get("data", {}).get("rows", [])
            etfs_df = pd.DataFrame(etfs_rows)

            if not etfs_df.empty:
                # Standardize ETF field names to match stocks schema
                field_mapping = {"companyName": "name", "lastSalePrice": "lastsale", "percentageChange": "pctchange"}

                # Rename columns based on mapping
                for old_col, new_col in field_mapping.items():
                    if old_col in etfs_df.columns:
                        etfs_df.rename(columns={old_col: new_col}, inplace=True)

                # Drop unnecessary ETF columns
                columns_to_drop = ["deltaIndicator", "oneYearPercentage"]
                etfs_df = etfs_df.drop(columns=[col for col in columns_to_drop if col in etfs_df.columns])

                # Add missing stock fields as empty strings for ETFs
                missing_fields = ["marketCap", "country", "ipoyear", "volume", "sector", "industry", "url"]
                for field in missing_fields:
                    if field not in etfs_df.columns:
                        etfs_df[field] = ""

                # Mark as ETF
                etfs_df["asset_type"] = "etf"

            # Combine the two dataframes
            combined_df = pd.concat([stocks_df, etfs_df], ignore_index=True)

            # Convert marketCap to numeric for stocks (ignore ETFs with empty marketCap)
            if "marketCap" in combined_df.columns:
                combined_df["marketCap"] = pd.to_numeric(combined_df["marketCap"], errors="coerce")

            return combined_df

        except Exception as e:
            logger.error(f"Error fetching NASDAQ screener data: {e}")
            return pd.DataFrame()

    def fetch_stock_news(self, symbol: str, days_back: int = 7) -> list[dict[str, str]]:
        """
        Fetch recent stock news for the given symbol.

        Args:
            symbol: Stock symbol
            days_back: Number of days to look back for news

        Returns:
            List[Dict]: List of news items
        """
        try:
            news_url = (
                f"https://www.nasdaq.com/api/news/topic/articlebysymbol?"
                f"q={symbol}|STOCKS&offset=0&limit=5&fallback=true"
            )
            json_data = fetch_nasdaq_api(news_url)
            data = json_data.get("data", {})
            if data is None:
                return []
            rows = data.get("rows", [])

            # Convert to DataFrame for efficient date filtering
            df = pd.DataFrame(rows)
            if df.empty:
                return []

            # Parse dates using pandas
            df["created_date"] = TimeSeriesProcessor.parse_financial_dates(df["created"].tolist(), ["%b %d, %Y"])

            # Filter recent news using pandas
            df_recent = TimeSeriesProcessor.filter_recent_data(df, "created_date", days_back)

            recent_news = []
            for _, row in df_recent.iterrows():
                news_url_field = row.get("url", "")
                full_url = get_full_url(news_url_field)
                news_item = {
                    "title": row.get("title", ""),
                    "created": row.get("created", ""),
                    "publisher": row.get("publisher", ""),
                    "url": full_url,
                }
                recent_news.append(news_item)

            return recent_news

        except Exception as e:
            logger.error(f"Error fetching stock news for {symbol}: {e}")
            return []

    def fetch_press_releases(self, symbol: str, days_back: int = 15) -> list[dict[str, str]]:
        """
        Fetch recent press releases for the given symbol.

        Args:
            symbol: Stock symbol
            days_back: Number of days to look back for press releases

        Returns:
            List[Dict]: List of press releases
        """
        try:
            url = (
                f"https://www.nasdaq.com/api/news/topic/press_release?"
                f"q=symbol:{symbol}|assetclass:stocks&limit=10&offset=0"
            )
            json_data = fetch_nasdaq_api(url)
            data = json_data.get("data", {})
            if data is None:
                return []
            rows = data.get("rows") or []

            recent_releases = []
            cutoff_date = datetime.now() - timedelta(days=days_back)

            for row in rows:
                created_date = safe_parse_date(row["created"], "%b %d, %Y")
                if not created_date or created_date < cutoff_date:
                    continue

                pr_url = row.get("url", "")
                full_url = get_full_url(pr_url)
                press_release = {
                    "title": row.get("title", ""),
                    "created": row.get("created", ""),
                    "publisher": row.get("publisher", ""),
                    "url": full_url,
                }
                recent_releases.append(press_release)

            return recent_releases

        except Exception as e:
            logger.error(f"Error fetching press releases for {symbol}: {e}")
            return []
