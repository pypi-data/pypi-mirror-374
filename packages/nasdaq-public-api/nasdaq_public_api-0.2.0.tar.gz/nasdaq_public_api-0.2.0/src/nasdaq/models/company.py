"""
Company profile dataclasses for NASDAQ API responses.
"""

from dataclasses import dataclass

from .base import BaseModel
from .base import parse_monetary_value


@dataclass
class CompanyProfile(BaseModel):
    """Company profile information from NASDAQ API."""

    symbol: str
    company_name: str
    description: str
    sector: str | None = None
    industry: str | None = None
    market_cap: float | None = None
    employees: int | None = None
    headquarters: str | None = None
    founded_year: int | None = None
    website: str | None = None
    phone: str | None = None
    address: str | None = None
    ceo: str | None = None
    asset_type: str = "stock"  # stock or etf

    def __post_init__(self):
        """Post-initialization processing for company profile data."""
        super().__post_init__()
        # Convert market cap if it's a string
        if isinstance(self.market_cap, str):
            self.market_cap = parse_monetary_value(self.market_cap)

        # Convert employee count if it's a string
        if isinstance(self.employees, str):
            try:
                # Remove commas and convert to int
                self.employees = int(self.employees.replace(",", ""))
            except (ValueError, AttributeError):
                self.employees = None

        # Convert founded year if it's a string
        if isinstance(self.founded_year, str):
            try:
                self.founded_year = int(self.founded_year)
            except (ValueError, AttributeError):
                self.founded_year = None

    @classmethod
    def from_dict(cls, data: dict) -> "CompanyProfile":
        """
        Create CompanyProfile instance from dictionary data.

        Args:
            data: Dictionary containing company profile data

        Returns:
            CompanyProfile instance
        """
        return cls(
            symbol=data.get("symbol", ""),
            company_name=data.get("company_name", ""),
            description=data.get("description", ""),
            sector=data.get("sector"),
            industry=data.get("industry"),
            market_cap=data.get("market_cap"),
            employees=data.get("employees"),
            headquarters=data.get("headquarters"),
            founded_year=data.get("founded_year"),
            website=data.get("website"),
            phone=data.get("phone"),
            address=data.get("address"),
            ceo=data.get("ceo"),
            asset_type=data.get("asset_type", "stock"),
        )
