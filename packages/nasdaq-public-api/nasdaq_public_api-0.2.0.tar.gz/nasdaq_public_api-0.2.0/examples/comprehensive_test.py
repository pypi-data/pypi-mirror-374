"""
Comprehensive test of the NASDAQ Public API Client.
Tests all available fetchers to verify functionality.
"""

import os
import sys

import pandas as pd


sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.nasdaq import NASDAQDataIngestor


def test_basic_functionality(ingestor):
    """Test basic NASDAQ API functionality."""
    print("=== Company Profile ===")
    profile = ingestor.fetch_company_profile("AAPL")
    print(f"Apple Inc. Profile: {profile[:100]}..." if profile else "No profile found")
    assert isinstance(profile, str), "Profile should be a string"

    print("\n=== Revenue and Earnings ===")
    revenue_data = ingestor.fetch_revenue_earnings("AAPL")
    print(f"Found {len(revenue_data)} quarters of revenue data")
    if revenue_data:
        print(f"Latest quarter: {revenue_data[-1]}")
    assert isinstance(revenue_data, list), "Revenue data should be a list"

    print("\n=== Historical Quotes ===")
    historical_data = ingestor.fetch_historical_quotes("AAPL", period=5)
    print(f"Found {len(historical_data)} days of historical data")
    if historical_data:
        latest_date = sorted(historical_data.keys())[-1]
        print(f"Latest closing price: {historical_data[latest_date].get('close')}")
    assert isinstance(historical_data, dict), "Historical data should be a dict"

    print("\n=== Earnings Calendar ===")
    earnings = ingestor.fetch_earnings_calendar(days_ahead=3)
    print(f"Found {len(earnings)} companies with upcoming earnings")
    if not earnings.empty:
        print(earnings.head())
    assert isinstance(earnings, pd.DataFrame), "Earnings should be a DataFrame"

    print("\n=== Dividend History ===")
    dividends = ingestor.fetch_dividend_history("AAPL")
    print(f"Found {len(dividends)} dividend records")
    if dividends:
        print(f"Latest dividend: {dividends[0] if dividends else 'None'}")
    assert isinstance(dividends, list), "Dividends should be a list"

    print("\n=== Financial Ratios ===")
    ratios = ingestor.fetch_financial_ratios("AAPL")
    print(f"Found {len(ratios)} financial ratios")
    if ratios:
        pe_ratio = ratios.get("P/E Ratio", {})
        print(f"P/E Ratio: {pe_ratio.get('displayValue', 'N/A')}")
    assert isinstance(ratios, dict), "Ratios should be a dict"

    print("\n=== Option Chain ===")
    options = ingestor.fetch_option_chain("AAPL")
    print(f"Option chain data retrieved: {'Yes' if options else 'No'}")
    assert isinstance(options, dict), "Options should be a dict"

    print("\n=== SEC Filings ===")
    sec_filings = ingestor.fetch_sec_filings("AAPL")
    print(f"Found {len(sec_filings)} SEC filings")
    if sec_filings:
        latest_filing = sec_filings[0] if sec_filings else {}
        filing_type = latest_filing.get("formType", "N/A")
        filing_date = latest_filing.get("filed", "N/A")
        print(f"Latest filing: {filing_type} filed on {filing_date}")
    assert isinstance(sec_filings, list), "SEC filings should be a list"

    return True


def test_enhanced_functionality(ingestor):
    """Test enhanced NASDAQ API functionality."""

    print("\n=== Insider Trading ===")
    insider_trading = ingestor.fetch_insider_trading("AAPL")
    if insider_trading:
        transaction_count = len(insider_trading.get("transaction_table", []))
        print(f"Insider trading data retrieved with {transaction_count} transactions")
    else:
        print("No insider trading data found")
    assert isinstance(insider_trading, dict), "Insider trading should be a dict"

    print("\n=== Institutional Holdings ===")
    institutional_holdings = ingestor.fetch_institutional_holdings("AAPL")
    if institutional_holdings:
        active_positions = institutional_holdings.get("active_positions", [])
        print(f"Institutional holdings data retrieved with {len(active_positions)} active positions")
    else:
        print("No institutional holdings data found")
    assert isinstance(institutional_holdings, dict), "Institutional holdings should be a dict"

    print("\n=== Short Interest ===")
    short_interest = ingestor.fetch_short_interest("AAPL")
    print(f"Found {len(short_interest)} short interest records")
    if short_interest:
        print(f"Latest short interest: {short_interest[0] if short_interest else 'None'}")
    assert isinstance(short_interest, list), "Short interest should be a list"

    print("\n=== NASDAQ Screener Data ===")
    screener_data = ingestor.fetch_nasdaq_screener_data()
    print(f"Found {len(screener_data)} screener records" if not screener_data.empty else "No screener data found")
    assert isinstance(screener_data, pd.DataFrame), "Screener data should be a DataFrame"

    print("\n=== Stock News ===")
    stock_news = ingestor.fetch_stock_news("AAPL", days_back=7)
    print(f"Found {len(stock_news)} news items")
    assert isinstance(stock_news, list), "Stock news should be a list"

    print("\n=== Press Releases ===")
    press_releases = ingestor.fetch_press_releases("AAPL", days_back=15)
    print(f"Found {len(press_releases)} press releases")
    assert isinstance(press_releases, list), "Press releases should be a list"

    return True


def main():
    """Demonstrate the usage of all NASDAQ API fetchers."""
    print("Initializing NASDAQ Data Ingestor...")

    # Initialize the data ingestor
    ingestor = NASDAQDataIngestor()

    print("Testing basic functionality...")
    basic_success = test_basic_functionality(ingestor)

    print("\nTesting enhanced functionality...")
    enhanced_success = test_enhanced_functionality(ingestor)

    if basic_success and enhanced_success:
        print("\n✅ All tests passed! The NASDAQ API client is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the output above.")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
