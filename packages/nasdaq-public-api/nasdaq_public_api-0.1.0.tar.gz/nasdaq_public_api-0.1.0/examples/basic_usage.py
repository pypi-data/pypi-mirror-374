"""
Example usage of the NASDAQ Public API Client.
"""

import os
import sys


sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src import NASDAQDataIngestor


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


if __name__ == "__main__":
    main()
