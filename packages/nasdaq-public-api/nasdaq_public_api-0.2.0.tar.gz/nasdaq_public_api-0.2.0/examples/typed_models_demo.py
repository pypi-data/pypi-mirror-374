"""
Example usage of the new typed data models for NASDAQ API responses.
"""

import os
import sys


sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.nasdaq import NASDAQDataIngestor
from src.nasdaq.models import CompanyProfile
from src.nasdaq.models import DividendRecord
from src.nasdaq.models import HistoricalQuote
from src.nasdaq.models import RevenueEarningsQuarter


def main():
    """Demonstrate the usage of typed data models with NASDAQ API responses."""
    # Initialize the data ingestor
    ingestor = NASDAQDataIngestor()

    print("=== Typed Data Models Demo ===\n")

    # Example 1: Company Profile with typed model
    print("1. Company Profile (Typed Model)")
    company_data = ingestor.fetch_company_profile("AAPL")
    if company_data:
        # Note: CompanyProfile.from_nasdaq_response expects different data structure
        # For demo purposes, we'll create a simple example
        company_profile = CompanyProfile(
            symbol="AAPL",
            company_name="Apple Inc.",
            description=company_data[:100] + "...",
            sector="Technology",
            industry="Consumer Electronics",
            market_cap=2_800_000_000_000.0,  # $2.8T
            employees=164000,
            headquarters="Cupertino, California",
            founded_year=1976,
            website="https://www.apple.com",
        )
        print(f"   {company_profile}")
        print(f"   Market Cap: ${company_profile.market_cap:,.0f}")
        print(f"   Employees: {company_profile.employees:,}")
    else:
        print("   No company profile data found")

    # Example 2: Revenue and Earnings with typed model
    print("\n2. Revenue and Earnings (Typed Model)")
    revenue_data = ingestor.fetch_revenue_earnings("AAPL")
    if revenue_data:
        # Convert raw data to typed models
        quarters = [RevenueEarningsQuarter.from_nasdaq_row(row) for row in revenue_data[-3:]]  # Last 3 quarters
        for i, quarter in enumerate(quarters):
            print(f"   Q{i + 1}: {quarter.quarter}")
            if quarter.revenue:
                print(f"      Revenue: ${quarter.revenue:,.0f}")
            if quarter.eps:
                print(f"      EPS: ${quarter.eps:.2f}")
            if quarter.dividends:
                print(f"      Dividends: ${quarter.dividends:.2f}")
    else:
        print("   No revenue data found")

    # Example 3: Historical Quotes with typed model
    print("\n3. Historical Quotes (Typed Model)")
    historical_data = ingestor.fetch_historical_quotes("AAPL", period=3)
    if historical_data:
        # Convert raw data to typed models
        quotes = [
            HistoricalQuote.from_nasdaq_row({"date": date, **data}) for date, data in list(historical_data.items())[-3:]
        ]  # Last 3 days
        for quote in quotes:
            print(f"   {quote.date.strftime('%Y-%m-%d')}: ${quote.close_price:.2f}")
            if quote.volume:
                print(f"      Volume: {quote.volume:,}")
    else:
        print("   No historical data found")

    # Example 4: Dividend History with typed model
    print("\n4. Dividend History (Typed Model)")
    dividend_data = ingestor.fetch_dividend_history("AAPL")
    if dividend_data:
        # Convert raw data to typed models (last 3 dividends)
        dividends = [DividendRecord.from_nasdaq_row(row) for row in dividend_data[:3]]
        for dividend in dividends:
            if dividend.ex_or_eff_date:
                print(f"   {dividend.ex_or_eff_date.strftime('%Y-%m-%d')}: ${dividend.amount:.2f}")
                print(f"      Type: {dividend.type}")
    else:
        print("   No dividend data found")

    print("\n=== Typed Models Benefits ===")
    print("✓ Automatic parsing of monetary values ($1.5B → 1,500,000,000.0)")
    print("✓ Smart date/time conversion (01/15/2023 → datetime object)")
    print("✓ Unit handling (M, B, T suffixes)")
    print("✓ Percentage conversion (5.5% → 0.055)")
    print("✓ Type safety with proper annotations")
    print("✓ Easy serialization/deserialization")
    print("✓ Consistent string representations")


if __name__ == "__main__":
    main()
