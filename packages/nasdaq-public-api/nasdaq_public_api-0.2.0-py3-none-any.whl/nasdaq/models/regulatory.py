"""
Regulatory dataclasses for NASDAQ API responses.
"""

from dataclasses import dataclass
from datetime import datetime

from .base import BaseModel
from .base import parse_datetime_value
from .base import parse_monetary_value


@dataclass
class SECFiling(BaseModel):
    """SEC filing record."""

    filing_type: str  # 10-K, 10-Q, 8-K, etc.
    filed_date: datetime
    acceptance_date: datetime | None = None
    period_of_report: datetime | None = None
    filing_date: datetime | None = None
    document_url: str | None = None
    description: str | None = None
    form_type: str | None = None
    size: str | None = None  # Size of the document

    def __post_init__(self):
        """Post-initialization processing for SEC filing data."""
        super().__post_init__()

        # Parse dates
        date_formats = ["%m/%d/%Y", "%Y-%m-%d", "%b %d, %Y"]

        if isinstance(self.filed_date, str):
            self.filed_date = parse_datetime_value(self.filed_date, date_formats)

        if isinstance(self.acceptance_date, str):
            self.acceptance_date = parse_datetime_value(self.acceptance_date, date_formats)

        if isinstance(self.period_of_report, str):
            self.period_of_report = parse_datetime_value(self.period_of_report, date_formats)

        if isinstance(self.filing_date, str):
            self.filing_date = parse_datetime_value(self.filing_date, date_formats)

    @classmethod
    def from_dict(cls, data: dict) -> "SECFiling":
        """
        Create SECFiling instance from dictionary data.

        Args:
            data: Dictionary containing SEC filing data

        Returns:
            SECFiling instance
        """
        # Extract filing type from various possible fields
        filing_type = (
            data.get("formType") or data.get("filingType") or data.get("filing_type") or data.get("type") or "Unknown"
        )

        # Extract filing date
        filed_date = data.get("filed") or data.get("filedDate") or data.get("date") or ""

        # Extract document URL from view object if present
        document_url = None
        if "view" in data and isinstance(data["view"], dict):
            document_url = data["view"].get("htmlLink") or data["view"].get("url") or data.get("url")
        else:
            document_url = data.get("url")

        # Parse dates
        date_formats = ["%m/%d/%Y", "%Y-%m-%d", "%b %d, %Y"]
        parsed_filed_date = parse_datetime_value(filed_date, date_formats)
        acceptance_date = parse_datetime_value(data.get("acceptanceDate"), date_formats)
        period_of_report = parse_datetime_value(data.get("periodOfReport"), date_formats)
        filing_date = parse_datetime_value(data.get("filingDate"), date_formats)

        return cls(
            filing_type=filing_type,
            filed_date=parsed_filed_date,
            acceptance_date=acceptance_date,
            period_of_report=period_of_report,
            filing_date=filing_date,
            document_url=document_url,
            description=data.get("description"),
            form_type=data.get("formType") or data.get("form_type") or data.get("filing_type"),
            size=data.get("size"),
        )


@dataclass
class EarningsCalendarEvent(BaseModel):
    """Earnings calendar event for a company."""

    symbol: str
    company_name: str
    earnings_date: datetime
    fiscal_quarter_ending: str
    eps_forecast: float | None = None
    eps_actual: float | None = None
    revenue_forecast: float | None = None
    revenue_actual: float | None = None
    number_of_estimates: int | None = None
    report_time: str = "Before Market Open"  # Before Market Open, After Market Close
    last_year_eps: float | None = None
    last_year_report_date: datetime | None = None

    def __post_init__(self):
        """Post-initialization processing for earnings calendar data."""
        super().__post_init__()

        # Parse dates
        date_formats = ["%m/%d/%Y", "%Y-%m-%d", "%b %d, %Y"]

        if isinstance(self.earnings_date, str):
            self.earnings_date = parse_datetime_value(self.earnings_date, date_formats)

        if isinstance(self.last_year_report_date, str):
            self.last_year_report_date = parse_datetime_value(self.last_year_report_date, date_formats)

        # Convert numerical values
        if isinstance(self.eps_forecast, str):
            try:
                # Handle negative values in parentheses
                if self.eps_forecast.startswith("(") and self.eps_forecast.endswith(")"):
                    self.eps_forecast = "-" + self.eps_forecast[1:-1]
                self.eps_forecast = float(self.eps_forecast.replace("$", ""))
            except (ValueError, AttributeError):
                self.eps_forecast = None

        if isinstance(self.eps_actual, str):
            try:
                # Handle negative values in parentheses
                if self.eps_actual.startswith("(") and self.eps_actual.endswith(")"):
                    self.eps_actual = "-" + self.eps_actual[1:-1]
                self.eps_actual = float(self.eps_actual.replace("$", ""))
            except (ValueError, AttributeError):
                self.eps_actual = None

        if isinstance(self.revenue_forecast, str):
            self.revenue_forecast = parse_monetary_value(self.revenue_forecast)

        if isinstance(self.revenue_actual, str):
            self.revenue_actual = parse_monetary_value(self.revenue_actual)

        if isinstance(self.number_of_estimates, str):
            try:
                self.number_of_estimates = int(self.number_of_estimates.replace(",", ""))
            except (ValueError, AttributeError):
                self.number_of_estimates = None

        if isinstance(self.last_year_eps, str):
            try:
                # Handle negative values in parentheses
                if self.last_year_eps.startswith("(") and self.last_year_eps.endswith(")"):
                    self.last_year_eps = "-" + self.last_year_eps[1:-1]
                self.last_year_eps = float(self.last_year_eps.replace("$", ""))
            except (ValueError, AttributeError):
                self.last_year_eps = None

    @classmethod
    def from_dict(cls, data: dict) -> "EarningsCalendarEvent":
        """
        Create EarningsCalendarEvent instance from dictionary data.

        Args:
            data: Dictionary containing earnings calendar data

        Returns:
            EarningsCalendarEvent instance
        """
        # Parse dates
        date_formats = ["%m/%d/%Y", "%Y-%m-%d", "%b %d, %Y"]
        earnings_date = parse_datetime_value(data.get("callDate") or data.get("earningsDate", ""), date_formats)
        last_year_report_date = parse_datetime_value(
            data.get("lastYearRptDt") or data.get("lastYearReportDate", ""), date_formats
        )

        return cls(
            symbol=data.get("symbol", ""),
            company_name=data.get("companyName", ""),
            earnings_date=earnings_date,
            fiscal_quarter_ending=data.get("fiscalQuarterEnding", ""),
            eps_forecast=data.get("epsForecast") or data.get("eps_forecast"),
            eps_actual=data.get("epsActual") or data.get("eps_actual"),
            revenue_forecast=data.get("revenueForecast") or data.get("revenue_forecast"),
            revenue_actual=data.get("revenueActual") or data.get("revenue_actual"),
            number_of_estimates=data.get("noOfEsts") or data.get("number_of_estimates"),
            report_time=data.get("time", "Before Market Open"),
            last_year_eps=data.get("lastYearEPS") or data.get("last_year_eps"),
            last_year_report_date=last_year_report_date,
        )
