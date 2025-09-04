"""
Command-line interface for the NASDAQ Public API Client.
"""

import argparse
import json
import sys

from nasdaq import NASDAQDataIngestor


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description='NASDAQ Public API Client')
    parser.add_argument('--symbol', '-s', help='Stock symbol to query')
    parser.add_argument('--period', '-p', type=int, default=30, help='Historical data period (days)')
    parser.add_argument('--days-ahead', '-d', type=int, default=7, help='Earnings calendar days ahead')
    parser.add_argument('--function', '-f', choices=[
        'profile', 'revenue', 'historical', 'insider', 'institutional',
        'short_interest', 'earnings', 'screener', 'news', 'press'
    ], required=True, help='Function to call')

    args = parser.parse_args()

    try:
        ingestor = NASDAQDataIngestor()

        if args.function == 'profile' and args.symbol:
            result = ingestor.fetch_company_profile(args.symbol)
            print(result)
        elif args.function == 'revenue' and args.symbol:
            result = ingestor.fetch_revenue_earnings(args.symbol)
            print(json.dumps(result, indent=2))
        elif args.function == 'historical' and args.symbol:
            result = ingestor.fetch_historical_quotes(args.symbol, period=args.period)
            print(json.dumps(result, indent=2))
        elif args.function == 'insider' and args.symbol:
            result = ingestor.fetch_insider_trading(args.symbol)
            print(json.dumps(result, indent=2))
        elif args.function == 'institutional' and args.symbol:
            result = ingestor.fetch_institutional_holdings(args.symbol)
            print(json.dumps(result, indent=2))
        elif args.function == 'short_interest' and args.symbol:
            result = ingestor.fetch_short_interest(args.symbol)
            print(json.dumps(result, indent=2))
        elif args.function == 'earnings':
            result = ingestor.fetch_earnings_calendar(days_ahead=args.days_ahead)
            print(result.to_json(indent=2))
        elif args.function == 'screener':
            result = ingestor.fetch_nasdaq_screener_data()
            print(result.to_json(indent=2))
        elif args.function == 'news' and args.symbol:
            result = ingestor.fetch_stock_news(args.symbol)
            for item in result:
                print(item)
        elif args.function == 'press' and args.symbol:
            result = ingestor.fetch_press_releases(args.symbol)
            for item in result:
                print(item)
        else:
            print(f"Invalid arguments for function: {args.function}")
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

