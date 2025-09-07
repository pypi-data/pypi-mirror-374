"""
Example usage of the NASDAQ Public API Client.
"""

import os
import sys


sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.nasdaq import NASDAQDataIngestor


def main():
    """Demonstrate the usage of the NASDAQ API client."""
    # Initialize the data ingestor
    ingestor = NASDAQDataIngestor()

    # Example 1: Get company profile
    print("=== Company Profile ===")
    profile = ingestor.fetch_company_profile("AAPL")
    print(f"Apple Inc. Profile: {profile[:100]}..." if profile else "No profile found")

    # Example 2: Get revenue and earnings
    print("\n=== Revenue and Earnings ===")
    revenue_data = ingestor.fetch_revenue_earnings("AAPL")
    print(f"Found {len(revenue_data)} quarters of revenue data")
    if revenue_data:
        print(f"Latest quarter: {revenue_data[-1]}")

    # Example 3: Get historical quotes
    print("\n=== Historical Quotes ===")
    historical_data = ingestor.fetch_historical_quotes("AAPL", period=5)
    print(f"Found {len(historical_data)} days of historical data")
    if historical_data:
        latest_date = sorted(historical_data.keys())[-1]
        print(f"Latest closing price: {historical_data[latest_date].get('close')}")

    # Example 4: Get earnings calendar
    print("\n=== Earnings Calendar ===")
    earnings = ingestor.fetch_earnings_calendar(days_ahead=3)
    print(f"Found {len(earnings)} companies with upcoming earnings")
    if not earnings.empty:
        print(earnings.head())

    # Example 5: Get dividend history
    print("\n=== Dividend History ===")
    dividends = ingestor.fetch_dividend_history("AAPL")
    print(f"Found {len(dividends)} dividend records")
    if dividends:
        print(f"Latest dividend: {dividends[0] if dividends else 'None'}")

    # Example 6: Get financial ratios
    print("\n=== Financial Ratios ===")
    ratios = ingestor.fetch_financial_ratios("AAPL")
    print(f"Found {len(ratios)} financial ratios")
    if ratios:
        # Try to get P/E Ratio, fallback to first available ratio
        pe_ratio = ratios.get("P/E Ratio", {}) or next(iter(ratios.values()), {})
        ratio_value = pe_ratio.get('displayValue', 'N/A')
        ratio_name = next((k for k, v in ratios.items() if v == pe_ratio), "P/E Ratio")
        print(f"{ratio_name}: {ratio_value}")
    else:
        print("No financial ratios found")

    # Example 7: Get option chain data
    print("\n=== Option Chain ===")
    options = ingestor.fetch_option_chain("AAPL")
    print(f"Option chain data retrieved: {'Yes' if options else 'No'}")

    # Example 8: Get SEC filings
    print("\n=== SEC Filings ===")
    sec_filings = ingestor.fetch_sec_filings("AAPL")
    print(f"Found {len(sec_filings)} SEC filings")
    if sec_filings:
        latest_filing = sec_filings[0] if sec_filings else {}
        filing_type = latest_filing.get("formType", "N/A")
        filing_date = latest_filing.get("filed", "N/A")
        print(f"Latest filing: {filing_type} filed on {filing_date}")


if __name__ == "__main__":
    main()


