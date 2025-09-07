"""
NASDAQ API Response Data Models
==============================

Dataclasses for structured, typed representations of NASDAQ API responses.
"""

from .base import BaseModel
from .company import CompanyProfile
from .financial import DividendRecord
from .financial import FinancialRatio
from .financial import HistoricalQuote
from .financial import OptionChainData
from .financial import RevenueEarningsQuarter
from .market import MarketScreenerResult
from .news import NewsArticle
from .news import PressRelease
from .ownership import InsiderTransaction
from .ownership import InstitutionalHolding
from .ownership import ShortInterestRecord
from .regulatory import EarningsCalendarEvent
from .regulatory import SECFiling


__all__ = [
    "BaseModel",
    "CompanyProfile",
    "DividendRecord",
    "EarningsCalendarEvent",
    "FinancialRatio",
    "HistoricalQuote",
    "InsiderTransaction",
    "InstitutionalHolding",
    "MarketScreenerResult",
    "NewsArticle",
    "OptionChainData",
    "PressRelease",
    "RevenueEarningsQuarter",
    "SECFiling",
    "ShortInterestRecord"
]
