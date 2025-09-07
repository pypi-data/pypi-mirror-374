"""
Financial dataclasses for NASDAQ API responses.
"""

from dataclasses import dataclass
from datetime import datetime

from .base import BaseModel
from .base import parse_datetime_value
from .base import parse_monetary_value


@dataclass
class RevenueEarningsQuarter(BaseModel):
    """Revenue and earnings data for a single quarter."""

    quarter: str
    revenue: float | None = None
    eps: float | None = None  # Earnings Per Share
    dividends: float | None = None
    fiscal_year: int | None = None
    fiscal_quarter: int | None = None

    def __post_init__(self):
        """Post-initialization processing for revenue/earnings data."""
        super().__post_init__()
        # Convert revenue if it's a string
        if isinstance(self.revenue, str):
            self.revenue = parse_monetary_value(self.revenue)

        # Convert EPS if it's a string
        if isinstance(self.eps, str):
            try:
                # Handle parentheses for negative values
                if self.eps.startswith("(") and self.eps.endswith(")"):
                    self.eps = "-" + self.eps[1:-1]
                self.eps = float(self.eps.replace("$", ""))
            except (ValueError, AttributeError):
                self.eps = None

        # Convert dividends if it's a string
        if isinstance(self.dividends, str):
            try:
                # Handle parentheses for negative values
                if self.dividends.startswith("(") and self.dividends.endswith(")"):
                    self.dividends = "-" + self.dividends[1:-1]
                self.dividends = float(self.dividends.replace("$", ""))
            except (ValueError, AttributeError):
                self.dividends = None

    @classmethod
    def from_dict(cls, data: dict) -> 'RevenueEarningsQuarter':
        """
        Create RevenueEarningsQuarter instance from dictionary data.

        Args:
            data: Dictionary containing revenue/earnings data

        Returns:
            RevenueEarningsQuarter instance
        """
        return cls(
            quarter=data.get("quarter", ""),
            revenue=data.get("revenue"),
            eps=data.get("eps"),
            dividends=data.get("dividends"),
            fiscal_year=data.get("fiscal_year"),
            fiscal_quarter=data.get("fiscal_quarter")
        )


@dataclass
class HistoricalQuote(BaseModel):
    """Historical stock price data for a single day."""

    date: datetime
    open_price: float | None = None
    high_price: float | None = None
    low_price: float | None = None
    close_price: float | None = None
    volume: int | None = None
    adjusted_close: float | None = None

    def __post_init__(self):
        """Post-initialization processing for historical quote data."""
        super().__post_init__()
        # Convert prices if they're strings
        for attr in ['open_price', 'high_price', 'low_price', 'close_price', 'adjusted_close']:
            value = getattr(self, attr)
            if isinstance(value, str):
                setattr(self, attr, parse_monetary_value(value))

        # Convert volume if it's a string
        if isinstance(self.volume, str):
            try:
                # Remove commas and convert to int
                self.volume = int(self.volume.replace(",", ""))
            except (ValueError, AttributeError):
                self.volume = None

    @classmethod
    def from_dict(cls, data: dict) -> 'HistoricalQuote':
        """
        Create HistoricalQuote instance from dictionary data.

        Args:
            data: Dictionary containing historical quote data

        Returns:
            HistoricalQuote instance
        """
        # Parse date
        date_formats = ["%m/%d/%Y", "%Y-%m-%d", "%b %d, %Y"]
        date_obj = parse_datetime_value(data.get("date"), date_formats)

        return cls(
            date=date_obj,
            open_price=data.get("open_price"),
            high_price=data.get("high_price"),
            low_price=data.get("low_price"),
            close_price=data.get("close_price"),
            volume=data.get("volume"),
            adjusted_close=data.get("adjusted_close")
        )


@dataclass
class DividendRecord(BaseModel):
    """Dividend payment record."""

    ex_or_eff_date: datetime  # Ex-dividend or effective date
    type: str  # Cash, Stock, Property, etc.
    amount: float | None = None
    declaration_date: datetime | None = None
    record_date: datetime | None = None
    payment_date: datetime | None = None
    currency: str = "USD"

    def __post_init__(self):
        """Post-initialization processing for dividend record data."""
        super().__post_init__()
        # Parse dates with common formats
        date_formats = ["%m/%d/%Y", "%Y-%m-%d", "%b %d, %Y"]

        if isinstance(self.ex_or_eff_date, str):
            self.ex_or_eff_date = parse_datetime_value(self.ex_or_eff_date, date_formats)

        if isinstance(self.declaration_date, str):
            self.declaration_date = parse_datetime_value(self.declaration_date, date_formats)

        if isinstance(self.record_date, str):
            self.record_date = parse_datetime_value(self.record_date, date_formats)

        if isinstance(self.payment_date, str):
            self.payment_date = parse_datetime_value(self.payment_date, date_formats)

        # Convert amount if it's a string
        if isinstance(self.amount, str):
            # Remove currency sign and convert to float
            try:
                self.amount = float(self.amount.replace("$", ""))
            except (ValueError, AttributeError):
                self.amount = None

    @classmethod
    def from_dict(cls, data: dict) -> 'DividendRecord':
        """
        Create DividendRecord instance from dictionary data.

        Args:
            data: Dictionary containing dividend record data

        Returns:
            DividendRecord instance
        """
        # Parse dates
        date_formats = ["%m/%d/%Y", "%Y-%m-%d", "%b %d, %Y"]
        ex_or_eff_date = parse_datetime_value(data.get("ex_or_eff_date") or data.get("date", ""), date_formats)
        declaration_date = parse_datetime_value(data.get("declaration_date"), date_formats)
        record_date = parse_datetime_value(data.get("record_date"), date_formats)
        payment_date = parse_datetime_value(data.get("payment_date"), date_formats)

        return cls(
            ex_or_eff_date=ex_or_eff_date,
            type=data.get("type", "Cash"),
            amount=data.get("amount"),
            declaration_date=declaration_date,
            record_date=record_date,
            payment_date=payment_date,
            currency=data.get("currency", "USD")
        )


@dataclass
class FinancialRatio(BaseModel):
    """Financial ratio data."""

    name: str
    value: float | None = None
    display_value: str = ""
    category: str | None = None  # Valuation, Profitability, Liquidity, etc.

    def __post_init__(self):
        """Post-initialization processing for financial ratio data."""
        super().__post_init__()
        # Convert value if it's a string
        if isinstance(self.value, str):
            # Remove percentage signs and convert to decimal
            try:
                cleaned_value = self.value.replace("%", "").replace(",", "")
                self.value = float(cleaned_value)
                # Convert percentage to decimal
                if "%" in self.value:
                    self.value = self.value / 100.0
            except (ValueError, AttributeError):
                self.value = None

    @classmethod
    def from_dict(cls, data: dict, category: str | None = None) -> 'FinancialRatio':
        """
        Create FinancialRatio instance from dictionary data.

        Args:
            data: Dictionary containing financial ratio data
            category: Optional category for the ratio

        Returns:
            FinancialRatio instance
        """
        # Extract value and display value
        value = data.get("value")
        display_value = data.get("display_value", "")

        # If no display value, use the raw value
        if not display_value and value:
            display_value = str(value)

        return cls(
            name=data.get("name", ""),
            value=value,
            display_value=display_value,
            category=category
        )


@dataclass
class OptionChainData(BaseModel):
    """Option chain data for calls and puts."""

    symbol: str
    expiration_date: datetime | None = None
    strike_price: float | None = None
    option_type: str = "Call"  # Call or Put
    last_price: float | None = None
    bid_price: float | None = None
    ask_price: float | None = None
    volume: int | None = None
    open_interest: int | None = None
    implied_volatility: float | None = None
    delta: float | None = None
    gamma: float | None = None
    theta: float | None = None
    vega: float | None = None

    def __post_init__(self):
        """Post-initialization processing for option chain data."""
        super().__post_init__()
        # Parse expiration date
        date_formats = ["%m/%d/%Y", "%Y-%m-%d", "%b %d, %Y"]
        if isinstance(self.expiration_date, str):
            self.expiration_date = parse_datetime_value(self.expiration_date, date_formats)

        # Convert monetary values
        monetary_attrs = ['strike_price', 'last_price', 'bid_price', 'ask_price']
        for attr in monetary_attrs:
            value = getattr(self, attr)
            if isinstance(value, str):
                setattr(self, attr, parse_monetary_value(value))

        # Convert integer values
        int_attrs = ['volume', 'open_interest']
        for attr in int_attrs:
            value = getattr(self, attr)
            if isinstance(value, str):
                try:
                    setattr(self, attr, int(value.replace(",", "")))
                except (ValueError, AttributeError):
                    setattr(self, attr, None)

        # Convert percentage values
        pct_attrs = ['implied_volatility']
        for attr in pct_attrs:
            value = getattr(self, attr)
            if isinstance(value, str):
                try:
                    # Remove % and convert to decimal
                    cleaned_value = value.replace("%", "")
                    setattr(self, attr, float(cleaned_value) / 100.0)
                except (ValueError, AttributeError):
                    setattr(self, attr, None)

    @classmethod
    def from_dict(cls, data: dict, symbol: str) -> 'OptionChainData':
        """
        Create OptionChainData instance from dictionary data.

        Args:
            data: Dictionary containing option chain data
            symbol: Stock symbol

        Returns:
            OptionChainData instance
        """
        # Parse expiration date
        date_formats = ["%m/%d/%Y", "%Y-%m-%d", "%b %d, %Y"]
        expiration_date = parse_datetime_value(data.get("expiration_date"), date_formats)

        return cls(
            symbol=symbol,
            expiration_date=expiration_date,
            strike_price=data.get("strike_price"),
            option_type=data.get("option_type", "Call"),
            last_price=data.get("last_price"),
            bid_price=data.get("bid_price"),
            ask_price=data.get("ask_price"),
            volume=data.get("volume"),
            open_interest=data.get("open_interest"),
            implied_volatility=data.get("implied_volatility"),
            delta=data.get("delta"),
            gamma=data.get("gamma"),
            theta=data.get("theta"),
            vega=data.get("vega")
        )
