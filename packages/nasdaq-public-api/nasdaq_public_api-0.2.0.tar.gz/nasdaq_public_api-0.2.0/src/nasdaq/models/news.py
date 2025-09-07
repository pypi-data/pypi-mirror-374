"""
News and press release dataclasses for NASDAQ API responses.
"""

from dataclasses import dataclass
from datetime import datetime

from .base import BaseModel
from .base import parse_datetime_value


@dataclass
class NewsArticle(BaseModel):
    """News article or press release."""

    title: str = ""
    created_date: datetime = datetime.min
    publisher: str = ""
    url: str = ""
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
    def from_nasdaq_row(cls, row_data: dict, symbol: str | None = None, article_type: str = "news") -> "NewsArticle":
        """
        Create NewsArticle instance from NASDAQ API row data.

        Args:
            row_data: Row data from NASDAQ API response
            symbol: Optional stock symbol
            article_type: Article type (news or press_release)

        Returns:
            NewsArticle instance
        """
        return cls(
            title=row_data.get("title", ""),
            created_date=row_data.get("created", ""),
            publisher=row_data.get("publisher", ""),
            url=row_data.get("url", ""),
            symbol=symbol,
            summary=row_data.get("summary") or row_data.get("description"),
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
        super().__post_init__()

    @classmethod
    def from_nasdaq_row(cls, row_data: dict, symbol: str | None = None) -> "PressRelease":
        """
        Create PressRelease instance from NASDAQ API row data.

        Args:
            row_data: Row data from NASDAQ API response
            symbol: Optional stock symbol

        Returns:
            PressRelease instance
        """
        return cls(
            title=row_data.get("title", ""),
            created_date=row_data.get("created", ""),
            publisher=row_data.get("publisher", ""),
            url=row_data.get("url", ""),
            symbol=symbol,
            summary=row_data.get("summary") or row_data.get("description"),
            article_type="press_release",
            contact_info=row_data.get("contactInfo") or row_data.get("contact_info"),
            release_type=row_data.get("releaseType") or row_data.get("release_type"),
        )

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
        created_date = parse_datetime_value(data.get("created_date") or data.get("created", ""), date_formats)

        return cls(
            title=data.get("title", ""),
            created_date=created_date,
            publisher=data.get("publisher", ""),
            url=data.get("url", ""),
            symbol=symbol,
            summary=data.get("summary") or data.get("description"),
            article_type="press_release",
            contact_info=data.get("contact_info") or data.get("contactInfo"),
            release_type=data.get("release_type") or data.get("releaseType"),
        )
