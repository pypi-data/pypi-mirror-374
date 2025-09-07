"""
Core module for NASDAQ cookie management.
"""

import logging
import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from ..config.settings import _last_cookie_refresh_time
from ..config.settings import _nasdaq_headers


logger = logging.getLogger(__name__)


# Constants
COOKIE_REFRESH_INTERVAL_SECONDS = 1800  # 30 minutes


def refresh_nasdaq_cookie(force: bool = False) -> bool:
    """
    Legacy function for backward compatibility.
    Uses Selenium to refresh NASDAQ cookies with enhanced browser simulation.

    Args:
        force: Force refresh even if cookies are still fresh

    Returns:
        bool: True if successful, False otherwise
    """
    if not force and _last_cookie_refresh_time is not None:
        time_since_refresh = datetime.now() - _last_cookie_refresh_time
        if time_since_refresh.total_seconds() < COOKIE_REFRESH_INTERVAL_SECONDS:  # 30 minutes
            return True

    # Reuse the cookie manager's configuration
    manager = NASDAQCookieManager()
    options = manager._configure_chrome_options()

    driver = None
    try:
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.get("https://www.nasdaq.com")
        time.sleep(10)

        # Try to interact with the page
        try:
            driver.execute_script("window.scrollTo(0, 100);")
            time.sleep(2)
        except Exception:
            pass

        cookies = driver.get_cookies()

        if not cookies:
            logger.warning("No cookies found from NASDAQ - proceeding without cookies")
            return True

        # Format cookies correctly
        cookie_str = manager._extract_cookies_string(cookies)
        _nasdaq_headers["cookie"] = cookie_str

        return True

    except Exception as e:
        logger.error(f"Error refreshing Nasdaq cookie: {e}")
        # Try to proceed without cookies
        return True
    finally:
        if driver:
            try:
                driver.quit()
            except Exception as e:
                logger.warning(f"Error closing webdriver: {e}")
                pass


class NASDAQCookieManager:
    """Manages NASDAQ cookie refresh for free data access."""

    def __init__(self, refresh_interval: int = COOKIE_REFRESH_INTERVAL_SECONDS):
        """
        Initialize NASDAQ cookie manager.

        Args:
            refresh_interval: Seconds between cookie refreshes (default: 30 minutes)
        """
        self.refresh_interval = refresh_interval
        self.last_refresh_time = None
        self.headers = _nasdaq_headers.copy()

    def needs_refresh(self) -> bool:
        """Check if cookies need to be refreshed."""
        if self.last_refresh_time is None:
            return True

        time_since_refresh = datetime.now() - self.last_refresh_time
        return time_since_refresh.total_seconds() > self.refresh_interval

    def _configure_chrome_options(self) -> Options:
        """Configure Chrome options with realistic browser simulation."""
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("--window-size=1920,1080")
        # Break long user agent string into multiple lines
        user_agent = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/138.0.0.0 Safari/537.36"
        )
        options.add_argument(f"--user-agent={user_agent}")
        return options

    def _extract_cookies_string(self, cookies: list) -> str:
        """Extract and format cookies for HTTP headers."""
        safe_pairs = []
        for cookie in cookies:
            name = cookie.get("name")
            val = cookie.get("value")
            if name is None or val is None:
                continue
            safe_pairs.append(f"{name}={val}")
        return "; ".join(safe_pairs)

    def refresh_cookies(self) -> bool:
        """
        Refresh NASDAQ cookies using Selenium with enhanced browser simulation.

        Returns:
            bool: True if cookies were successfully refreshed, False otherwise
        """
        if not self.needs_refresh():
            logger.debug("Cookies are still fresh, skipping refresh")
            return True

        logger.info("Refreshing NASDAQ cookies...")

        driver = None
        try:
            options = self._configure_chrome_options()
            driver = webdriver.Chrome(options=options)

            # Execute script to hide webdriver property
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            # Navigate to NASDAQ homepage
            logger.debug("Navigating to NASDAQ homepage...")
            driver.get("https://www.nasdaq.com")

            # Wait longer for page to load and cookies to be set
            time.sleep(10)

            # Try to interact with the page to trigger cookie setting
            try:
                driver.execute_script("window.scrollTo(0, 100);")
                time.sleep(2)
            except Exception:
                pass

            # Extract cookies
            cookies = driver.get_cookies()
            if not cookies:
                logger.warning("No cookies found from NASDAQ - trying fallback approach")
                # Try without cookies for now - some APIs might still work
                self.headers.pop("cookie", None)  # Remove any old cookie

                logger.info("Proceeding without cookies - some functionality may be limited")
                return True

            # Format cookies for HTTP headers
            cookie_str = self._extract_cookies_string(cookies)
            self.headers["cookie"] = cookie_str

            logger.info(f"Successfully refreshed {len(cookies)} NASDAQ cookies")
            return True

        except Exception as e:
            logger.error(f"Error refreshing NASDAQ cookies: {e}")
            # Try to proceed without cookies
            logger.info("Attempting to proceed without cookies")
            return True

        finally:
            if driver:
                try:
                    driver.quit()
                except Exception as e:
                    logger.warning(f"Error closing webdriver: {e}")
