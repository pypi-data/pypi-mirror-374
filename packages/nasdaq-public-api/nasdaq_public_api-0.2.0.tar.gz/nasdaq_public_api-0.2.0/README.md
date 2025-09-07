# NASDAQ Public API Client

[![PyPI version](https://badge.fury.io/py/nasdaq-public-api.svg)](https://badge.fury.io/py/nasdaq-public-api)
[![Python Version](https://img.shields.io/pypi/pyversions/nasdaq-public-api.svg)](https://pypi.org/project/nasdaq-public-api/)
[![License](https://img.shields.io/pypi/l/nasdaq-public-api.svg)](https://github.com/your-username/nasdaq-public-api/blob/main/LICENSE)

A minimal Python client for accessing NASDAQ's public API. This library automates cookie management and provides easy access to market data without requiring an API key.

## Features

- Automated cookie management using Selenium
- Access to company profiles and financial data
- Historical stock price retrieval
- Insider trading and institutional holdings data
- Earnings calendar and short interest information
- Stock screener for stocks and ETFs
- News and press release retrieval
- Typed dataclasses for all API responses
- Automatic data parsing and conversion
- Proper financial data handling with units and currencies
- Optimized data processing with pandas

## Installation

```bash
pip install nasdaq-public-api
```

## Quick Start

```python
from nasdaq import NASDAQDataIngestor

# Initialize the data ingestor
ingestor = NASDAQDataIngestor()

# Get company profile
profile = ingestor.fetch_company_profile("AAPL")
print(profile)

# Get historical stock prices
historical_data = ingestor.fetch_historical_quotes("AAPL", period=30)
print(historical_data)

# Get earnings calendar
earnings = ingestor.fetch_earnings_calendar(days_ahead=7)
print(earnings)
```

## Typed Data Models

The library includes comprehensive dataclasses for all NASDAQ API responses with automatic parsing and conversion:

```python
from nasdaq import NASDAQDataIngestor
from nasdaq.models import CompanyProfile, HistoricalQuote, DividendRecord

# Initialize the data ingestor
ingestor = NASDAQDataIngestor()

# Get typed company profile
company_data = ingestor.fetch_company_profile("AAPL")
company_profile = CompanyProfile.from_nasdaq_response(company_data, "AAPL")
print(company_profile)
# CompanyProfile(symbol=AAPL, company_name=Apple Inc., ...)

# Get typed historical quotes with automatic parsing
historical_raw = ingestor.fetch_historical_quotes("AAPL", period=5)
quotes = [HistoricalQuote.from_nasdaq_row(row) for row in historical_raw.values()]
print(quotes[0])
# HistoricalQuote(date=2023-01-15 00:00:00, open_price=175.4, ...)

# Get typed dividend records with unit conversion
dividends_raw = ingestor.fetch_dividend_history("AAPL")
dividends = [DividendRecord.from_nasdaq_row(row) for row in dividends_raw]
print(dividends[0])
# DividendRecord(ex_or_eff_date=2023-02-10 00:00:00, amount=0.23, ...)
```

## Available Data Models

### Financial Data
- `CompanyProfile` - Company information and fundamentals
- `RevenueEarningsQuarter` - Quarterly revenue and earnings
- `HistoricalQuote` - Daily stock price data
- `DividendRecord` - Dividend payment history
- `FinancialRatio` - Financial ratios and metrics
- `OptionChainData` - Call and put option chains

### Ownership Data
- `InsiderTransaction` - Corporate insider trading records
- `InstitutionalHolding` - Institutional investor holdings
- `ShortInterestRecord` - Short selling activity

### Regulatory Data
- `SECFiling` - SEC filing records
- `EarningsCalendarEvent` - Earnings announcements
- `MarketScreenerResult` - Stock and ETF screening results

### News Data
- `NewsArticle` - Financial news articles
- `PressRelease` - Corporate press releases

## Automatic Data Processing Features

### Monetary Value Parsing
```python
# Automatically converts:
"$1.5B" → 1_500_000_000.0
"$2.3M" → 2_300_000.0
"5.5%" → 0.055
"(100,000)" → -100000.0
```

### Date/Time Parsing
```python
# Automatically parses:
"01/15/2023" → datetime(2023, 1, 15)
"Jan 15, 2023" → datetime(2023, 1, 15)
"2023-01-15" → datetime(2023, 1, 15)
```

### Unit Conversions
```python
# Automatically handles:
"M" → Millions (1_000_000)
"B" → Billions (1_000_000_000)
"T" → Trillions (1_000_000_000_000)
```

## Requirements

- Python 3.12+
- Chrome browser (for cookie management)
- ChromeDriver (automatically managed)

## API Reference

### NASDAQDataIngestor

#### `fetch_company_profile(symbol: str) -> str`
Fetch company description for a given stock symbol.

#### `fetch_revenue_earnings(symbol: str) -> list[dict]`
Fetch revenue and earnings data for the last 6 quarters.

#### `fetch_historical_quotes(symbol: str, period: int = 5, asset_class: str = "stock") -> dict`
Fetch historical prices for a given stock symbol.

#### `fetch_insider_trading(symbol: str) -> dict`
Fetch insider trading data for a given stock symbol.

#### `fetch_institutional_holdings(symbol: str) -> dict`
Fetch institutional holdings data for a given stock symbol.

#### `fetch_short_interest(symbol: str) -> list[dict]`
Fetch short interest data for a given stock symbol.

#### `fetch_earnings_calendar(days_ahead: int = 7) -> pandas.DataFrame`
Fetch earnings calendar for upcoming days.

#### `fetch_nasdaq_screener_data() -> pandas.DataFrame`
Fetch both NASDAQ stock and ETF data.

#### `fetch_stock_news(symbol: str, days_back: int = 7) -> list[str]`
Fetch recent stock news for a given symbol.

#### `fetch_press_releases(symbol: str, days_back: int = 15) -> list[str]`
Fetch recent press releases for a given symbol.

#### `fetch_dividend_history(symbol: str) -> list[dict]`
Fetch dividend history data for the given stock symbol.

#### `fetch_financial_ratios(symbol: str) -> dict`
Fetch financial ratios data for the given stock symbol.

#### `fetch_option_chain(symbol: str, money_type: str = "ALL") -> dict`
Fetch option chain data for the given stock symbol.

#### `fetch_sec_filings(symbol: str, filing_type: str = "ALL") -> list[dict]`
Fetch SEC filings data for the given stock symbol.

## Data Processing Utilities

The package also includes optimized data processing utilities in the `data_processing` module:

- `DataProcessing`: General data manipulation functions
- `FinancialDataProcessor`: Specialized financial data aggregation
- `TimeSeriesProcessor`: Time series-specific operations
- `LargeDatasetProcessor`: Optimized processing for large datasets

## Configuration

The library can be configured through environment variables:

- `NASDAQ_COOKIE_REFRESH_INTERVAL`: Cookie refresh interval in seconds (default: 1800)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This library is for educational and research purposes only. Please obey all applicable laws and terms of service when using this library. The authors are not responsible for any misuse of this software.

## Caveats

⚠️ **Rate Limiting**: NASDAQ may impose rate limits on API access. Use responsibly.

⚠️ **Data Accuracy**: This library provides access to publicly available data. Verify critical information through official sources.

⚠️ **Terms of Service**: Ensure compliance with NASDAQ's terms of service when using this library.

⚠️ **Browser Automation**: The library uses Selenium for cookie management, which requires Chrome and may be affected by browser updates.

⚠️ **API Changes**: NASDAQ may change their API structure, potentially breaking functionality.

⚠️ **Typed Models**: The new typed dataclasses are additive and don't change existing API behavior. They provide enhanced functionality for developers who want stronger typing and automatic data parsing.