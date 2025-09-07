"""
Test suite for NASDAQ API response dataclasses.
"""

import unittest
from datetime import datetime

from src.nasdaq.models.base import parse_datetime_value
from src.nasdaq.models.base import parse_monetary_value
from src.nasdaq.models.company import CompanyProfile
from src.nasdaq.models.financial import DividendRecord
from src.nasdaq.models.financial import HistoricalQuote
from src.nasdaq.models.financial import RevenueEarningsQuarter
from src.nasdaq.models.market import MarketScreenerResult
from src.nasdaq.models.news import NewsArticle
from src.nasdaq.models.news import PressRelease
from src.nasdaq.models.ownership import InsiderTransaction
from src.nasdaq.models.ownership import InstitutionalHolding
from src.nasdaq.models.ownership import ShortInterestRecord
from src.nasdaq.models.regulatory import EarningsCalendarEvent
from src.nasdaq.models.regulatory import SECFiling


class TestBaseModels(unittest.TestCase):
    """Test base model functionality."""

    def test_monetary_value_parser(self):
        """Test monetary value parsing function."""
        # Test basic values
        self.assertEqual(parse_monetary_value(None), None)
        self.assertEqual(parse_monetary_value(""), None)
        self.assertEqual(parse_monetary_value("N/A"), None)
        self.assertEqual(parse_monetary_value(100), 100.0)
        self.assertEqual(parse_monetary_value(100.50), 100.50)
        self.assertEqual(parse_monetary_value("100"), 100.0)
        self.assertEqual(parse_monetary_value("$100"), 100.0)
        self.assertEqual(parse_monetary_value("$1,000"), 1000.0)

        # Test units
        self.assertEqual(parse_monetary_value("$1.5M"), 1_500_000.0)
        self.assertEqual(parse_monetary_value("$2.3B"), 2_300_000_000.0)
        self.assertEqual(parse_monetary_value("$1.2T"), 1_200_000_000_000.0)

        # Test percentages
        self.assertEqual(parse_monetary_value("5.5%"), 0.055)
        self.assertEqual(parse_monetary_value("100%"), 1.0)

    def test_datetime_value_parser(self):
        """Test datetime value parsing function."""
        formats = ["%m/%d/%Y", "%Y-%m-%d", "%b %d, %Y"]

        # Test basic values
        self.assertEqual(parse_datetime_value(None, formats), None)
        self.assertEqual(parse_datetime_value("", formats), None)
        dt = datetime(2023, 1, 15)
        self.assertEqual(parse_datetime_value(dt, formats), dt)

        # Test string parsing
        parsed_dt = parse_datetime_value("01/15/2023", formats)
        self.assertEqual(parsed_dt.year, 2023)
        self.assertEqual(parsed_dt.month, 1)
        self.assertEqual(parsed_dt.day, 15)


class TestCompanyModels(unittest.TestCase):
    """Test company profile dataclasses."""

    def test_company_profile(self):
        """Test company profile model."""
        # Test creation from dict
        data = {
            "symbol": "AAPL",
            "company_name": "Apple Inc.",
            "description": "Apple designs a wide variety of consumer electronic devices.",
            "sector": "Technology",
            "industry": "Consumer Electronics",
            "market_cap": "$2.5T",
            "employees": "164,000",
            "headquarters": "Cupertino, California",
            "founded_year": "1976",
            "website": "https://www.apple.com",
            "phone": "(408) 996-1010",
            "address": "One Apple Park Way",
            "ceo": "Tim Cook",
        }

        profile = CompanyProfile.from_dict(data)
        self.assertEqual(profile.symbol, "AAPL")
        self.assertEqual(profile.company_name, "Apple Inc.")
        self.assertEqual(profile.description, "Apple designs a wide variety of consumer electronic devices.")
        self.assertEqual(profile.sector, "Technology")
        self.assertEqual(profile.industry, "Consumer Electronics")
        self.assertEqual(profile.website, "https://www.apple.com")
        self.assertEqual(profile.phone, "(408) 996-1010")
        self.assertEqual(profile.address, "One Apple Park Way")
        self.assertEqual(profile.ceo, "Tim Cook")

        # Test string representation
        str_repr = str(profile)
        self.assertIn("AAPL", str_repr)
        self.assertIn("Apple Inc.", str_repr)


class TestFinancialModels(unittest.TestCase):
    """Test financial dataclasses."""

    def test_revenue_earnings_quarter(self):
        """Test revenue and earnings quarter model."""
        data = {
            "quarter": "Q1 2023",
            "revenue": "$117.15B",
            "eps": "$1.52",
            "dividends": "$0.23",
            "fiscal_year": 2023,
            "fiscal_quarter": 1,
        }

        q = RevenueEarningsQuarter.from_dict(data)
        self.assertEqual(q.quarter, "Q1 2023")
        self.assertEqual(q.revenue, 117_150_000_000.0)
        self.assertEqual(q.eps, 1.52)
        self.assertEqual(q.dividends, 0.23)
        self.assertEqual(q.fiscal_year, 2023)
        self.assertEqual(q.fiscal_quarter, 1)

    def test_historical_quote(self):
        """Test historical quote model."""
        data = {
            "date": "01/15/2023",
            "open_price": "$175.40",
            "high_price": "$178.30",
            "low_price": "$174.20",
            "close_price": "$177.80",
            "volume": "45,678,912",
            "adjusted_close": "$177.80",
        }

        quote = HistoricalQuote.from_dict(data)
        self.assertEqual(quote.open_price, 175.40)
        self.assertEqual(quote.high_price, 178.30)
        self.assertEqual(quote.low_price, 174.20)
        self.assertEqual(quote.close_price, 177.80)
        self.assertEqual(quote.volume, 45678912)

    def test_dividend_record(self):
        """Test dividend record model."""
        data = {
            "ex_or_eff_date": "02/10/2023",
            "type": "Cash",
            "amount": "$0.23",
            "declaration_date": "12/01/2022",
            "record_date": "02/13/2023",
            "payment_date": "02/16/2023",
            "currency": "USD",
        }

        div = DividendRecord.from_dict(data)
        self.assertEqual(div.type, "Cash")
        self.assertEqual(div.amount, 0.23)
        self.assertEqual(div.currency, "USD")


class TestOwnershipModels(unittest.TestCase):
    """Test ownership dataclasses."""

    def test_insider_transaction(self):
        """Test insider transaction model."""
        data = {
            "transaction_date": "01/15/2023",
            "insider_name": "Cook, Timothy D.",
            "relationship": "CEO",
            "transaction_type": "Purchase",
            "shares": "10,000",
            "price_per_share": "$175.40",
            "total_value": "$1.75M",
            "shares_owned_after": "1,000,000",
            "filing_date": "01/17/2023",
        }

        transaction = InsiderTransaction.from_dict(data)
        self.assertEqual(transaction.insider_name, "Cook, Timothy D.")
        self.assertEqual(transaction.relationship, "CEO")
        self.assertEqual(transaction.transaction_type, "Purchase")
        self.assertEqual(transaction.shares, 10000)
        self.assertEqual(transaction.price_per_share, 175.40)
        self.assertEqual(transaction.total_value, 1_750_000.0)

    def test_institutional_holding(self):
        """Test institutional holding model."""
        data = {
            "institution_name": "Vanguard Group Inc.",
            "shares_held": "1,000,000",
            "market_value": "$175.4M",
            "weight_percent": "5.5%",
            "change_in_shares": "100,000",
            "change_percent": "11.1%",
            "last_reported_date": "12/31/2022",
        }

        holding = InstitutionalHolding.from_dict(data)
        self.assertEqual(holding.institution_name, "Vanguard Group Inc.")
        self.assertEqual(holding.shares_held, 1_000_000)
        self.assertEqual(holding.market_value, 175_400_000.0)
        self.assertEqual(holding.weight_percent, 0.055)

    def test_short_interest_record(self):
        """Test short interest record model."""
        data = {
            "settlement_date": "01/15/2023",
            "short_interest": "50,000,000",
            "average_daily_volume": "25,000,000",
            "days_to_cover": "2.0",
        }

        record = ShortInterestRecord.from_dict(data)
        self.assertEqual(record.short_interest, 50_000_000)
        self.assertEqual(record.average_daily_volume, 25_000_000)
        self.assertEqual(record.days_to_cover, 2.0)


class TestRegulatoryModels(unittest.TestCase):
    """Test regulatory dataclasses."""

    def test_sec_filing(self):
        """Test SEC filing model."""
        data = {
            "filing_type": "10-K",
            "filed_date": "10/28/2022",
            "acceptance_date": "10/28/2022",
            "period_of_report": "09/24/2022",
            "document_url": "https://www.sec.gov/Archives/edgar/data/...",
            "description": "Annual report pursuant to Section 13 or 15(d)",
            "form_type": "10-K",
            "size": "10.5 MB",
        }

        filing = SECFiling.from_dict(data)
        self.assertEqual(filing.filing_type, "10-K")
        self.assertEqual(filing.form_type, "10-K")
        self.assertEqual(filing.size, "10.5 MB")

    def test_earnings_calendar_event(self):
        """Test earnings calendar event model."""
        data = {
            "symbol": "AAPL",
            "company_name": "Apple Inc.",
            "earnings_date": "01/25/2023",
            "fiscal_quarter_ending": "12/31/2022",
            "eps_forecast": "$1.43",
            "eps_actual": "$1.52",
            "revenue_forecast": "$117.0B",
            "revenue_actual": "$117.15B",
            "number_of_estimates": "12",
            "report_time": "After Market Close",
            "last_year_eps": "$1.39",
            "last_year_report_date": "01/27/2022",
        }

        event = EarningsCalendarEvent.from_dict(data)
        self.assertEqual(event.symbol, "AAPL")
        self.assertEqual(event.eps_forecast, 1.43)
        self.assertEqual(event.eps_actual, 1.52)
        self.assertEqual(event.revenue_forecast, 117_000_000_000.0)

    def test_market_screener_result(self):
        """Test market screener result model."""
        data = {
            "symbol": "AAPL",
            "company_name": "Apple Inc.",
            "last_sale_price": "$177.80",
            "net_change": "$2.50",
            "percentage_change": "1.43%",
            "market_cap": "$2.8T",
            "country": "United States",
            "ipo_year": "1980",
            "volume": "45,678,912",
            "sector": "Technology",
            "industry": "Consumer Electronics",
            "asset_type": "stock",
        }

        result = MarketScreenerResult.from_dict(data)
        self.assertEqual(result.symbol, "AAPL")
        self.assertEqual(result.last_sale_price, 177.80)
        self.assertEqual(result.percentage_change, 0.0143)
        self.assertEqual(result.market_cap, 2_800_000_000_000.0)


class TestNewsModels(unittest.TestCase):
    """Test news dataclasses."""

    def test_news_article(self):
        """Test news article model."""
        data = {
            "title": "Apple Announces Strong Quarterly Earnings",
            "created_date": "01/25/2023",
            "publisher": "Reuters",
            "url": "https://www.reuters.com/article/apple-earnings...",
            "symbol": "AAPL",
            "summary": "Apple reported strong quarterly earnings...",
            "article_type": "news",
        }

        article = NewsArticle.from_dict(data)
        self.assertEqual(article.title, "Apple Announces Strong Quarterly Earnings")
        self.assertEqual(article.publisher, "Reuters")
        self.assertEqual(article.article_type, "news")

    def test_press_release(self):
        """Test press release model."""
        data = {
            "title": "Apple Reports Record Quarterly Revenue",
            "created_date": "01/25/2023",
            "publisher": "Apple Inc.",
            "url": "https://www.apple.com/newsroom/2023/01/apple-reports...",
            "symbol": "AAPL",
            "summary": "Apple today announced quarterly revenue of $117.15 billion...",
            "article_type": "press_release",
            "contact_info": "investor.relations@apple.com",
            "release_type": "Earnings",
        }

        release = PressRelease.from_dict(data)
        self.assertEqual(release.title, "Apple Reports Record Quarterly Revenue")
        self.assertEqual(release.release_type, "Earnings")
        self.assertEqual(release.contact_info, "investor.relations@apple.com")


if __name__ == "__main__":
    unittest.main()
