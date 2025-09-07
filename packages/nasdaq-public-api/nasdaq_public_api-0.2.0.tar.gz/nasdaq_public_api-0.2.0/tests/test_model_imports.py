"""
Simple test to verify all NASDAQ API response models can be imported and instantiated.
"""

import os
import sys
from datetime import datetime


sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.nasdaq.models import CompanyProfile
from src.nasdaq.models import DividendRecord
from src.nasdaq.models import EarningsCalendarEvent
from src.nasdaq.models import FinancialRatio
from src.nasdaq.models import HistoricalQuote
from src.nasdaq.models import InsiderTransaction
from src.nasdaq.models import InstitutionalHolding
from src.nasdaq.models import MarketScreenerResult
from src.nasdaq.models import NewsArticle
from src.nasdaq.models import OptionChainData
from src.nasdaq.models import PressRelease
from src.nasdaq.models import RevenueEarningsQuarter
from src.nasdaq.models import SECFiling
from src.nasdaq.models import ShortInterestRecord


def test_all_models():
    """Test that all models can be imported and instantiated."""
    print("Testing NASDAQ API Response Models...")

    # Test CompanyProfile
    company = CompanyProfile(symbol="AAPL", company_name="Apple Inc.", description="Technology company")
    print(f"✓ CompanyProfile: {company}")

    # Test RevenueEarningsQuarter
    revenue_q = RevenueEarningsQuarter(quarter="Q1 2023", revenue=117_150_000_000.0, eps=1.52, dividends=0.23)
    print(f"✓ RevenueEarningsQuarter: {revenue_q}")

    # Test HistoricalQuote
    quote = HistoricalQuote(
        date=datetime(2023, 1, 15),
        open_price=175.40,
        high_price=178.30,
        low_price=174.20,
        close_price=177.80,
        volume=45678912,
    )
    print(f"✓ HistoricalQuote: {quote}")

    # Test DividendRecord
    dividend = DividendRecord(
        ex_or_eff_date=datetime(2023, 2, 10),
        type="Cash",
        amount=0.23,
        declaration_date=datetime(2022, 12, 1),
        record_date=datetime(2023, 2, 13),
        payment_date=datetime(2023, 2, 16),
    )
    print(f"✓ DividendRecord: {dividend}")

    # Test FinancialRatio
    ratio = FinancialRatio(name="P/E Ratio", value=28.5, display_value="28.5", category="Valuation")
    print(f"✓ FinancialRatio: {ratio}")

    # Test OptionChainData
    option = OptionChainData(
        symbol="AAPL",
        expiration_date=datetime(2023, 3, 15),
        strike_price=180.0,
        option_type="Call",
        last_price=5.25,
        bid_price=5.20,
        ask_price=5.30,
        volume=12500,
        open_interest=45000,
    )
    print(f"✓ OptionChainData: {option}")

    # Test InsiderTransaction
    insider = InsiderTransaction(
        transaction_date=datetime(2023, 1, 15),
        insider_name="Cook, Timothy D.",
        relationship="CEO",
        transaction_type="Purchase",
        shares=10000,
        price_per_share=175.40,
        total_value=1_754_000.0,
        shares_owned_after=1000000,
    )
    print(f"✓ InsiderTransaction: {insider}")

    # Test InstitutionalHolding
    institution = InstitutionalHolding(
        institution_name="Vanguard Group Inc.",
        shares_held=1000000,
        market_value=175_400_000.0,
        weight_percent=0.055,
        change_in_shares=100000,
        change_percent=0.111,
    )
    print(f"✓ InstitutionalHolding: {institution}")

    # Test ShortInterestRecord
    short_interest = ShortInterestRecord(
        settlement_date=datetime(2023, 1, 15), short_interest=50000000, average_daily_volume=25000000, days_to_cover=2.0
    )
    print(f"✓ ShortInterestRecord: {short_interest}")

    # Test SECFiling
    sec_filing = SECFiling(
        filing_type="10-K",
        filed_date=datetime(2022, 10, 28),
        acceptance_date=datetime(2022, 10, 28),
        period_of_report=datetime(2022, 9, 24),
        document_url="https://www.sec.gov/Archives/edgar/data/...",
    )
    print(f"✓ SECFiling: {sec_filing}")

    # Test EarningsCalendarEvent
    earnings_event = EarningsCalendarEvent(
        symbol="AAPL",
        company_name="Apple Inc.",
        earnings_date=datetime(2023, 1, 25),
        fiscal_quarter_ending="12/31/2022",
        eps_forecast=1.43,
        eps_actual=1.52,
        revenue_forecast=117_000_000_000.0,
        revenue_actual=117_150_000_000.0,
    )
    print(f"✓ EarningsCalendarEvent: {earnings_event}")

    # Test MarketScreenerResult
    screener_result = MarketScreenerResult(
        symbol="AAPL",
        company_name="Apple Inc.",
        last_sale_price=177.80,
        net_change=2.50,
        percentage_change=0.0143,
        market_cap=2_800_000_000_000.0,
        country="United States",
        ipo_year=1980,
        volume=45678912,
        sector="Technology",
        industry="Consumer Electronics",
    )
    print(f"✓ MarketScreenerResult: {screener_result}")

    # Test NewsArticle
    news = NewsArticle(
        title="Apple Announces Strong Quarterly Earnings",
        created_date=datetime(2023, 1, 25),
        publisher="Reuters",
        url="https://www.reuters.com/article/apple-earnings...",
        symbol="AAPL",
        summary="Apple reported strong quarterly earnings...",
    )
    print(f"✓ NewsArticle: {news}")

    # Test PressRelease
    press_release = PressRelease(
        title="Apple Reports Record Quarterly Revenue",
        created_date=datetime(2023, 1, 25),
        publisher="Apple Inc.",
        url="https://www.apple.com/newsroom/2023/01/apple-reports...",
        symbol="AAPL",
        summary="Apple today announced quarterly revenue of $117.15 billion...",
        article_type="press_release",
        contact_info="investor.relations@apple.com",
        release_type="Earnings",
    )
    print(f"✓ PressRelease: {press_release}")

    print("\n🎉 All NASDAQ API Response Models working correctly!")


if __name__ == "__main__":
    test_all_models()
