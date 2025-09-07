"""
Market dataclasses for NASDAQ API responses.
"""

from dataclasses import dataclass
from datetime import datetime

from .base import BaseModel
from .base import parse_datetime_value
from .base import parse_monetary_value


@dataclass
class MarketScreenerResult(BaseModel):
    """Market screener result for a stock or ETF."""

    symbol: str
    company_name: str
    last_sale_price: float | None = None
    net_change: float | None = None
    percentage_change: float | None = None  # Decimal format (0.05 = 5%)
    market_cap: float | None = None
    country: str | None = None
    ipo_year: int | None = None
    volume: int | None = None
    sector: str | None = None
    industry: str | None = None
    asset_type: str = "stock"  # stock or etf

    def __post_init__(self):
        """Post-initialization processing for market screener data."""
        super().__post_init__()

        # Convert monetary values
        if isinstance(self.last_sale_price, str):
            self.last_sale_price = parse_monetary_value(self.last_sale_price)

        if isinstance(self.net_change, str):
            try:
                # Handle negative values in parentheses
                if self.net_change.startswith("(") and self.net_change.endswith(")"):
                    self.net_change = "-" + self.net_change[1:-1]
                self.net_change = float(self.net_change.replace("$", ""))
            except (ValueError, AttributeError):
                self.net_change = None

        if isinstance(self.percentage_change, str):
            try:
                # Remove % and convert to decimal
                cleaned_value = self.percentage_change.replace("%", "")
                self.percentage_change = float(cleaned_value) / 100.0
            except (ValueError, AttributeError):
                self.percentage_change = None

        if isinstance(self.market_cap, str):
            self.market_cap = parse_monetary_value(self.market_cap)

        if isinstance(self.ipo_year, str):
            try:
                self.ipo_year = int(self.ipo_year)
            except (ValueError, AttributeError):
                self.ipo_year = None

        if isinstance(self.volume, str):
            try:
                # Remove commas and convert to int
                self.volume = int(self.volume.replace(",", ""))
            except (ValueError, AttributeError):
                self.volume = None

    @classmethod
    def from_dict(cls, data: dict, asset_type: str = "stock") -> "MarketScreenerResult":
        """
        Create MarketScreenerResult instance from dictionary data.

        Args:
            data: Dictionary containing market screener data
            asset_type: Asset type (stock or etf)

        Returns:
            MarketScreenerResult instance
        """
        return cls(
            symbol=data.get("symbol", ""),
            company_name=(data.get("name") or data.get("companyName", "")),
            last_sale_price=data.get("lastsale") or data.get("lastSalePrice") or data.get("last_sale_price"),
            net_change=data.get("netchange") or data.get("netChange") or data.get("net_change"),
            percentage_change=data.get("pctchange") or data.get("percentageChange") or data.get("percentage_change"),
            market_cap=data.get("marketCap") or data.get("market_cap"),
            country=data.get("country"),
            ipo_year=data.get("ipoyear") or data.get("ipoYear") or data.get("ipo_year"),
            volume=data.get("volume"),
            sector=data.get("sector"),
            industry=data.get("industry"),
            asset_type=asset_type,
        )


@dataclass
class NewsArticle(BaseModel):
    """News article or press release."""

    title: str
    created_date: datetime
    publisher: str
    url: str
    symbol: str | None = None
    summary: str | None = None
    article_type: str = "news"  # news or press_release

    def __post_init__(self):
        """Post-initialization processing for news article data."""
        super().__post_init__()

        # Parse date
        date_formats = ["%m/%d/%Y", "%Y-%m-%d", "%b %d, %Y", "%Y-%m-%dT%H:%M:%S"]
        if isinstance(self.created_date, str):
            self.created_date = parse_datetime_value(self.created_date, date_formats)

    @classmethod
    def from_dict(cls, data: dict, symbol: str | None = None, article_type: str = "news") -> "NewsArticle":
        """
        Create NewsArticle instance from dictionary data.

        Args:
            data: Dictionary containing news article data
            symbol: Optional stock symbol
            article_type: Article type (news or press_release)

        Returns:
            NewsArticle instance
        """
        # Parse date
        date_formats = ["%m/%d/%Y", "%Y-%m-%d", "%b %d, %Y", "%Y-%m-%dT%H:%M:%S"]
        created_date = parse_datetime_value(data.get("created", ""), date_formats)

        return cls(
            title=data.get("title", ""),
            created_date=created_date,
            publisher=data.get("publisher", ""),
            url=data.get("url", ""),
            symbol=symbol,
            summary=data.get("summary") or data.get("description"),
            article_type=article_type,
        )


@dataclass
class PressRelease(NewsArticle):
    """Press release, inheriting from NewsArticle."""

    # Press releases might have additional fields specific to corporate announcements
    contact_info: str | None = None
    release_type: str | None = None  # Earnings, Acquisition, Partnership, etc.

    def __post_init__(self):
        """Post-initialization processing for press release data."""
        # Call parent post_init if needed
        super().__post_init__()

    @classmethod
    def from_dict(cls, data: dict, symbol: str | None = None) -> "PressRelease":
        """
        Create PressRelease instance from dictionary data.

        Args:
            data: Dictionary containing press release data
            symbol: Optional stock symbol

        Returns:
            PressRelease instance
        """
        # Parse date
        date_formats = ["%m/%d/%Y", "%Y-%m-%d", "%b %d, %Y", "%Y-%m-%dT%H:%M:%S"]
        created_date = parse_datetime_value(data.get("created", ""), date_formats)

        return cls(
            title=data.get("title", ""),
            created_date=created_date,
            publisher=data.get("publisher", ""),
            url=data.get("url", ""),
            symbol=symbol,
            summary=data.get("summary") or data.get("description"),
            article_type="press_release",
            contact_info=data.get("contactInfo") or data.get("contact_info"),
            release_type=data.get("releaseType") or data.get("release_type"),
        )
