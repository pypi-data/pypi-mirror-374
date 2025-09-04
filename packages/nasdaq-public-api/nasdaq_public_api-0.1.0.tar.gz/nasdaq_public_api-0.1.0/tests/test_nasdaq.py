"""
Tests for the NASDAQ data ingestion module.
"""

import unittest
from unittest.mock import MagicMock
from unittest.mock import patch

from src.nasdaq import NASDAQCookieManager
from src.nasdaq import NASDAQDataIngestor
from src.nasdaq import safe_get_nested


class TestNASDAQCookieManager(unittest.TestCase):
    """Tests for the NASDAQCookieManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.cookie_manager = NASDAQCookieManager()

    def test_needs_refresh_initial(self):
        """Test that cookies need refresh initially."""
        assert self.cookie_manager.needs_refresh()

    @patch('src.nasdaq.webdriver')
    def test_refresh_cookies_success(self, mock_webdriver):
        """Test successful cookie refresh."""
        # Mock the webdriver and its methods
        mock_driver = MagicMock()
        mock_webdriver.Chrome.return_value = mock_driver
        mock_driver.get_cookies.return_value = [
            {'name': 'test_cookie', 'value': 'test_value'}
        ]

        result = self.cookie_manager.refresh_cookies()
        assert result


class TestNASDAQDataIngestor(unittest.TestCase):
    """Tests for the NASDAQDataIngestor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.ingestor = NASDAQDataIngestor()

    @patch('src.nasdaq.fetch_nasdaq_api')
    def test_fetch_company_profile_success(self, mock_fetch):
        """Test successful company profile fetch."""
        # Mock the API response
        mock_fetch.return_value = {
            'data': {
                'CompanyDescription': {
                    'value': 'Test company description'
                }
            }
        }

        result = self.ingestor.fetch_company_profile('TEST')
        assert result == 'Test company description'

    @patch('src.nasdaq.fetch_nasdaq_api')
    def test_fetch_company_profile_no_data(self, mock_fetch):
        """Test company profile fetch with no data."""
        mock_fetch.return_value = {'data': None}

        result = self.ingestor.fetch_company_profile('TEST')
        assert result == ''

    def test_safe_get_nested(self):
        """Test the safe_get_nested helper function."""

        test_data = {
            'level1': {
                'level2': {
                    'value': 'test'
                }
            }
        }

        result = safe_get_nested(test_data, 'level1', 'level2', 'value')
        assert result == 'test'

        result = safe_get_nested(test_data, 'level1', 'missing', default='default')
        assert result == 'default'


if __name__ == '__main__':
    unittest.main()

