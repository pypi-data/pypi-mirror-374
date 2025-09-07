"""
Ownership dataclasses for NASDAQ API responses.
"""

from dataclasses import dataclass
from datetime import datetime

from .base import BaseModel
from .base import parse_datetime_value
from .base import parse_monetary_value


@dataclass
class InsiderTransaction(BaseModel):
    """Insider trading transaction record."""

    transaction_date: datetime
    insider_name: str
    relationship: str  # Officer, Director, 10% Owner, etc.
    transaction_type: str  # Purchase, Sale, Option Exercise, etc.
    shares: int | None = None
    price_per_share: float | None = None
    total_value: float | None = None
    shares_owned_after: int | None = None
    filing_date: datetime | None = None

    def __post_init__(self):
        """Post-initialization processing for insider transaction data."""
        super().__post_init__()

        # Parse dates with common formats
        date_formats = ["%m/%d/%Y", "%Y-%m-%d", "%b %d, %Y"]

        if isinstance(self.transaction_date, str):
            self.transaction_date = parse_datetime_value(self.transaction_date, date_formats)

        if isinstance(self.filing_date, str):
            self.filing_date = parse_datetime_value(self.filing_date, date_formats)

        # Convert numerical values
        if isinstance(self.shares, str):
            try:
                self.shares = int(self.shares.replace(",", ""))
            except (ValueError, AttributeError):
                self.shares = None

        if isinstance(self.price_per_share, str):
            self.price_per_share = parse_monetary_value(self.price_per_share)

        if isinstance(self.total_value, str):
            self.total_value = parse_monetary_value(self.total_value)

        if isinstance(self.shares_owned_after, str):
            try:
                self.shares_owned_after = int(self.shares_owned_after.replace(",", ""))
            except (ValueError, AttributeError):
                self.shares_owned_after = None

    @classmethod
    def from_dict(cls, data: dict) -> "InsiderTransaction":
        """
        Create InsiderTransaction instance from dictionary data.

        Args:
            data: Dictionary containing insider transaction data

        Returns:
            InsiderTransaction instance
        """
        # Parse dates
        date_formats = ["%m/%d/%Y", "%Y-%m-%d", "%b %d, %Y"]
        transaction_date = parse_datetime_value(data.get("transaction_date") or data.get("date", ""), date_formats)
        filing_date = parse_datetime_value(data.get("filing_date"), date_formats)

        # Convert numerical values
        shares = data.get("shares")
        if isinstance(shares, str):
            try:
                shares = int(shares.replace(",", ""))
            except (ValueError, AttributeError):
                shares = None

        price_per_share = data.get("price_per_share")
        if isinstance(price_per_share, str):
            price_per_share = parse_monetary_value(price_per_share)

        total_value = data.get("total_value")
        if isinstance(total_value, str):
            total_value = parse_monetary_value(total_value)

        shares_owned_after = data.get("shares_owned_after")
        if isinstance(shares_owned_after, str):
            try:
                shares_owned_after = int(shares_owned_after.replace(",", ""))
            except (ValueError, AttributeError):
                shares_owned_after = None

        return cls(
            transaction_date=transaction_date,
            insider_name=data.get("insider_name", ""),
            relationship=data.get("relationship", ""),
            transaction_type=data.get("transaction_type", ""),
            shares=shares,
            price_per_share=price_per_share,
            total_value=total_value,
            shares_owned_after=shares_owned_after,
            filing_date=filing_date,
        )


@dataclass
class InstitutionalHolding(BaseModel):
    """Institutional investor holding record."""

    institution_name: str
    shares_held: int | None = None
    market_value: float | None = None
    weight_percent: float | None = None  # Percentage of portfolio
    change_in_shares: int | None = None
    change_percent: float | None = None  # Percentage change
    last_reported_date: datetime | None = None

    def __post_init__(self):
        """Post-initialization processing for institutional holding data."""
        super().__post_init__()

        # Parse date
        date_formats = ["%m/%d/%Y", "%Y-%m-%d", "%b %d, %Y"]
        if isinstance(self.last_reported_date, str):
            self.last_reported_date = parse_datetime_value(self.last_reported_date, date_formats)

        # Convert numerical values
        if isinstance(self.shares_held, str):
            try:
                # Remove commas and convert to int
                self.shares_held = int(self.shares_held.replace(",", ""))
            except (ValueError, AttributeError):
                self.shares_held = None

        if isinstance(self.market_value, str):
            self.market_value = parse_monetary_value(self.market_value)

        if isinstance(self.weight_percent, str):
            try:
                # Remove % and convert to decimal
                cleaned_value = self.weight_percent.replace("%", "")
                self.weight_percent = float(cleaned_value) / 100.0
            except (ValueError, AttributeError):
                self.weight_percent = None

        if isinstance(self.change_in_shares, str):
            try:
                # Handle negative values in parentheses
                if self.change_in_shares.startswith("(") and self.change_in_shares.endswith(")"):
                    self.change_in_shares = "-" + self.change_in_shares[1:-1]
                self.change_in_shares = int(self.change_in_shares.replace(",", ""))
            except (ValueError, AttributeError):
                self.change_in_shares = None

        if isinstance(self.change_percent, str):
            try:
                # Remove % and convert to decimal
                cleaned_value = self.change_percent.replace("%", "")
                self.change_percent = float(cleaned_value) / 100.0
            except (ValueError, AttributeError):
                self.change_percent = None

    @classmethod
    def from_dict(cls, data: dict) -> "InstitutionalHolding":
        """
        Create InstitutionalHolding instance from dictionary data.

        Args:
            data: Dictionary containing institutional holding data

        Returns:
            InstitutionalHolding instance
        """
        # Parse date
        date_formats = ["%m/%d/%Y", "%Y-%m-%d", "%b %d, %Y"]
        last_reported_date = parse_datetime_value(data.get("last_reported_date") or data.get("date", ""), date_formats)

        # Convert numerical values
        shares_held = data.get("shares_held")
        if isinstance(shares_held, str):
            try:
                shares_held = int(shares_held.replace(",", ""))
            except (ValueError, AttributeError):
                shares_held = None

        market_value = data.get("market_value")
        if isinstance(market_value, str):
            market_value = parse_monetary_value(market_value)

        weight_percent = data.get("weight_percent")
        if isinstance(weight_percent, str):
            try:
                # Remove % and convert to decimal
                cleaned_value = weight_percent.replace("%", "")
                weight_percent = float(cleaned_value) / 100.0
            except (ValueError, AttributeError):
                weight_percent = None

        change_in_shares = data.get("change_in_shares")
        if isinstance(change_in_shares, str):
            try:
                # Handle negative values in parentheses
                if change_in_shares.startswith("(") and change_in_shares.endswith(")"):
                    change_in_shares = "-" + change_in_shares[1:-1]
                change_in_shares = int(change_in_shares.replace(",", ""))
            except (ValueError, AttributeError):
                change_in_shares = None

        change_percent = data.get("change_percent")
        if isinstance(change_percent, str):
            try:
                # Remove % and convert to decimal
                cleaned_value = change_percent.replace("%", "")
                change_percent = float(cleaned_value) / 100.0
            except (ValueError, AttributeError):
                change_percent = None

        return cls(
            institution_name=data.get("institution_name", ""),
            shares_held=shares_held,
            market_value=market_value,
            weight_percent=weight_percent,
            change_in_shares=change_in_shares,
            change_percent=change_percent,
            last_reported_date=last_reported_date,
        )


@dataclass
class ShortInterestRecord(BaseModel):
    """Short interest record for a settlement date."""

    settlement_date: datetime
    short_interest: int | None = None
    average_daily_volume: int | None = None
    days_to_cover: float | None = None  # Days to cover short interest at average volume

    def __post_init__(self):
        """Post-initialization processing for short interest data."""
        super().__post_init__()

        # Parse date
        date_formats = ["%m/%d/%Y", "%Y-%m-%d", "%b %d, %Y"]
        if isinstance(self.settlement_date, str):
            self.settlement_date = parse_datetime_value(self.settlement_date, date_formats)

        # Convert numerical values
        if isinstance(self.short_interest, str):
            try:
                # Remove commas and convert to int
                self.short_interest = int(self.short_interest.replace(",", ""))
            except (ValueError, AttributeError):
                self.short_interest = None

        if isinstance(self.average_daily_volume, str):
            try:
                # Remove commas and convert to int
                self.average_daily_volume = int(self.average_daily_volume.replace(",", ""))
            except (ValueError, AttributeError):
                self.average_daily_volume = None

        if isinstance(self.days_to_cover, str):
            try:
                self.days_to_cover = float(self.days_to_cover)
            except (ValueError, AttributeError):
                self.days_to_cover = None

    @classmethod
    def from_dict(cls, data: dict) -> "ShortInterestRecord":
        """
        Create ShortInterestRecord instance from dictionary data.

        Args:
            data: Dictionary containing short interest data

        Returns:
            ShortInterestRecord instance
        """
        # Parse date
        date_formats = ["%m/%d/%Y", "%Y-%m-%d", "%b %d, %Y"]
        settlement_date = parse_datetime_value(data.get("settlement_date") or data.get("date", ""), date_formats)

        # Convert numerical values
        short_interest = data.get("short_interest") or data.get("interest")
        if isinstance(short_interest, str):
            try:
                # Remove commas and convert to int
                short_interest = int(short_interest.replace(",", ""))
            except (ValueError, AttributeError):
                short_interest = None

        average_daily_volume = data.get("average_daily_volume") or data.get("avgDailyShareVolume")
        if isinstance(average_daily_volume, str):
            try:
                # Remove commas and convert to int
                average_daily_volume = int(average_daily_volume.replace(",", ""))
            except (ValueError, AttributeError):
                average_daily_volume = None

        days_to_cover = data.get("days_to_cover")
        if isinstance(days_to_cover, str):
            try:
                days_to_cover = float(days_to_cover)
            except (ValueError, AttributeError):
                days_to_cover = None

        return cls(
            settlement_date=settlement_date,
            short_interest=short_interest,
            average_daily_volume=average_daily_volume,
            days_to_cover=days_to_cover,
        )
