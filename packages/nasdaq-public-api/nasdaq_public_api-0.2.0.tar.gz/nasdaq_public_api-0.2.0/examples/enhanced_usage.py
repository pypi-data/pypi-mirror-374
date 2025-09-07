"""
Enhanced example usage of the NASDAQ Public API Client.
Tests all available fetchers to identify issues.
"""

import os
import sys


sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.nasdaq import NASDAQDataIngestor


def test_basic_fetchers(ingestor):
    """Test basic NASDAQ API fetchers."""
    print("=== Company Profile ===")
    profile = ingestor.fetch_company_profile("AAPL")
    print(f"Apple Inc. Profile: {profile[:100]}..." if profile else "No profile found")

    print("\n=== Revenue and Earnings ===")
    revenue_data = ingestor.fetch_revenue_earnings("AAPL")
    print(f"Found {len(revenue_data)} quarters of revenue data")
    if revenue_data:
        print(f"Latest quarter: {revenue_data[-1]}")

    print("\n=== Historical Quotes ===")
    historical_data = ingestor.fetch_historical_quotes("AAPL", period=5)
    print(f"Found {len(historical_data)} days of historical data")
    if historical_data:
        latest_date = sorted(historical_data.keys())[-1]
        print(f"Latest closing price: {historical_data[latest_date].get('close')}")

    print("\n=== Earnings Calendar ===")
    earnings = ingestor.fetch_earnings_calendar(days_ahead=3)
    print(f"Found {len(earnings)} companies with upcoming earnings")
    if not earnings.empty:
        print(earnings.head())

    print("\n=== Dividend History ===")
    dividends = ingestor.fetch_dividend_history("AAPL")
    print(f"Found {len(dividends)} dividend records")
    if dividends:
        print(f"Latest dividend: {dividends[0] if dividends else 'None'}")

    print("\n=== Financial Ratios ===")
    ratios = ingestor.fetch_financial_ratios("AAPL")
    print(f"Found {len(ratios)} financial ratios")
    if ratios:
        pe_ratio = ratios.get("P/E Ratio", {})
        print(f"P/E Ratio: {pe_ratio.get('displayValue', 'N/A')}")

    print("\n=== Option Chain ===")
    options = ingestor.fetch_option_chain("AAPL")
    print(f"Option chain data retrieved: {'Yes' if options else 'No'}")

    print("\n=== SEC Filings ===")
    sec_filings = ingestor.fetch_sec_filings("AAPL")
    print(f"Found {len(sec_filings)} SEC filings")
    if sec_filings:
        latest_filing = sec_filings[0] if sec_filings else {}
        filing_type = latest_filing.get("filingType", "N/A")
        filing_date = latest_filing.get("filedDate", "N/A")
        print(f"Latest filing: {filing_type} filed on {filing_date}")


def test_enhanced_fetchers(ingestor):
    """Test enhanced NASDAQ API fetchers."""
    # Additional fetchers not in basic example:

    print("\n=== Insider Trading ===")
    insider_trading = ingestor.fetch_insider_trading("AAPL")
    if insider_trading:
        print(f"Insider trading data retrieved with {len(insider_trading.get('transaction_table', []))} transactions")
    else:
        print("No insider trading data found")

    print("\n=== Institutional Holdings ===")
    institutional_holdings = ingestor.fetch_institutional_holdings("AAPL")
    if institutional_holdings:
        active_positions = institutional_holdings.get("active_positions", [])
        print(f"Institutional holdings data retrieved with {len(active_positions)} active positions")
    else:
        print("No institutional holdings data found")

    print("\n=== Short Interest ===")
    short_interest = ingestor.fetch_short_interest("AAPL")
    print(f"Found {len(short_interest)} short interest records")
    if short_interest:
        print(f"Latest short interest: {short_interest[0] if short_interest else 'None'}")

    print("\n=== NASDAQ Screener Data ===")
    screener_data = ingestor.fetch_nasdaq_screener_data()
    print(f"Found {len(screener_data)} screener records" if not screener_data.empty else "No screener data found")

    print("\n=== Stock News ===")
    stock_news = ingestor.fetch_stock_news("AAPL", days_back=7)
    print(f"Found {len(stock_news)} news items")

    print("\n=== Press Releases ===")
    press_releases = ingestor.fetch_press_releases("AAPL", days_back=15)
    print(f"Found {len(press_releases)} press releases")


def main():
    """Demonstrate the usage of all NASDAQ API fetchers."""
    # Initialize the data ingestor
    ingestor = NASDAQDataIngestor()

    print("Testing all NASDAQ API fetchers...\n")

    test_basic_fetchers(ingestor)
    test_enhanced_fetchers(ingestor)


if __name__ == "__main__":
    main()
