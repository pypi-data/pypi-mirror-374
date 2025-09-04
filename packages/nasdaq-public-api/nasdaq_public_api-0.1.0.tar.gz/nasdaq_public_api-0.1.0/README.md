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