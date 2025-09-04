"""
NASDAQ data ingestion module using cookie-based authentication.

This module provides free access to NASDAQ data by refreshing cookies
from their public website using Selenium automation.
"""

import json
import logging
import time
from datetime import datetime
from datetime import timedelta
from typing import Any

import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from .data_processing import TimeSeriesProcessor


logger = logging.getLogger(__name__)

# Global state for cookie management
_last_cookie_refresh_time: datetime | None = None
_nasdaq_headers: dict[str, str] = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-GB,en;q=0.9,en-US;q=0.8",
    "cache-control": "max-age=0",
    "dnt": "1",
    "priority": "u=0, i",
    "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Microsoft Edge";v="132"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
}


class NASDAQCookieManager:
    """Manages NASDAQ cookie refresh for free data access."""

    def __init__(self, refresh_interval: int = 1800):
        """
        Initialize NASDAQ cookie manager.

        Args:
            refresh_interval: Seconds between cookie refreshes (default: 30 minutes)
        """
        self.refresh_interval = refresh_interval
        self.last_refresh_time: datetime | None = None
        self.headers = _nasdaq_headers.copy()

    def needs_refresh(self) -> bool:
        """Check if cookies need to be refreshed."""
        if self.last_refresh_time is None:
            return True

        time_since_refresh = datetime.now() - self.last_refresh_time
        return time_since_refresh.total_seconds() > self.refresh_interval

    def refresh_cookies(self) -> bool:
        """
        Refresh NASDAQ cookies using Selenium with enhanced browser simulation.

        Returns:
            bool: True if cookies were successfully refreshed, False otherwise
        """
        global _last_cookie_refresh_time, _nasdaq_headers

        if not self.needs_refresh():
            logger.debug("Cookies are still fresh, skipping refresh")
            return True

        logger.info("Refreshing NASDAQ cookies...")

        # Configure Chrome options with more realistic browser simulation
        options = Options()
        options.add_argument("--headless=new")  # Use new headless mode
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("--window-size=1920,1080")

        # Add realistic user agent
        options.add_argument(
            "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
        )

        driver = None
        try:
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
            except:
                pass

            # Extract cookies
            cookies = driver.get_cookies()
            if not cookies:
                logger.warning("No cookies found from NASDAQ - trying fallback approach")
                # Try without cookies for now - some APIs might still work
                self.headers.pop("cookie", None)  # Remove any old cookie

                # Update global state even without cookies
                _last_cookie_refresh_time = datetime.now()
                self.last_refresh_time = _last_cookie_refresh_time
                _nasdaq_headers.update(self.headers)

                logger.info("Proceeding without cookies - some functionality may be limited")
                return True

            # Format cookies for HTTP headers - use the working approach
            safe_pairs = []
            for cookie in cookies:
                name = cookie.get("name")
                val = cookie.get("value")
                if name is None or val is None:
                    continue
                safe_pairs.append(f"{name}={val}")
            cookie_str = "; ".join(safe_pairs)
            self.headers["cookie"] = cookie_str

            # Update global state
            _last_cookie_refresh_time = datetime.now()
            self.last_refresh_time = _last_cookie_refresh_time
            _nasdaq_headers.update(self.headers)

            logger.info(f"Successfully refreshed {len(cookies)} NASDAQ cookies")
            return True

        except Exception as e:
            logger.error(f"Error refreshing NASDAQ cookies: {e}")
            # Try to proceed without cookies
            logger.info("Attempting to proceed without cookies")
            _last_cookie_refresh_time = datetime.now()
            self.last_refresh_time = _last_cookie_refresh_time
            return True

        finally:
            if driver:
                try:
                    driver.quit()
                except Exception as e:
                    logger.warning(f"Error closing webdriver: {e}")

    def get_headers(self) -> dict[str, str]:
        """
        Get HTTP headers with fresh cookies for NASDAQ requests.

        Returns:
            Dict[str, str]: HTTP headers including fresh cookies
        """
        if self.needs_refresh():
            self.refresh_cookies()

        return self.headers.copy()


def get_nasdaq_headers(refresh_interval: int = 1800) -> dict[str, str]:
    """
    Convenience function to get NASDAQ headers with fresh cookies.

    Args:
        refresh_interval: Seconds between cookie refreshes

    Returns:
        Dict[str, str]: HTTP headers for NASDAQ requests
    """
    # Refresh cookies if needed
    refresh_nasdaq_cookie()
    return _nasdaq_headers.copy()


def refresh_nasdaq_cookie(force: bool = False) -> bool:
    """
    Legacy function for backward compatibility.
    Uses Selenium to refresh NASDAQ cookies with enhanced browser simulation.

    Args:
        force: Force refresh even if cookies are still fresh

    Returns:
        bool: True if successful, False otherwise
    """
    global _last_cookie_refresh_time, _nasdaq_headers

    if not force and _last_cookie_refresh_time is not None:
        time_since_refresh = datetime.now() - _last_cookie_refresh_time
        if time_since_refresh.total_seconds() < 1800:  # 30 minutes
            return True

    # Enhanced Chrome options for better cookie retrieval
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
    )

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
        except:
            pass

        cookies = driver.get_cookies()

        if not cookies:
            logger.warning("No cookies found from NASDAQ - proceeding without cookies")
            _last_cookie_refresh_time = datetime.now()
            return True

        # Format cookies correctly - use lowercase 'cookie' key
        safe_pairs = []
        for cookie in cookies:
            name = cookie.get("name")
            val = cookie.get("value")
            if name is None or val is None:
                continue
            safe_pairs.append(f"{name}={val}")
        cookie_str = "; ".join(safe_pairs)
        _nasdaq_headers["cookie"] = cookie_str
        _last_cookie_refresh_time = datetime.now()

        logger.info(f"Successfully refreshed {len(cookies)} NASDAQ cookies")
        return True

    except Exception as e:
        logger.error(f"Error refreshing Nasdaq cookie: {e}")
        # Try to proceed without cookies
        _last_cookie_refresh_time = datetime.now()
        return True
    finally:
        if driver:
            try:
                driver.quit()
            except Exception as e:
                logger.warning(f"Error closing webdriver: {e}")
                pass


def safe_get_nested(data: dict, *keys: str, default: Any = None) -> Any:
    """
    Safely access nested dictionary values without raising AttributeError.

    Args:
        data: The dictionary to traverse
        *keys: The keys to access in order
        default: Default value if path doesn't exist

    Returns:
        The value at the nested location or default if not found
    """
    try:
        for key in keys:
            if not isinstance(data, dict):
                return default
            data = data.get(key, default)
        return data
    except AttributeError:
        return default


def safe_parse_date(date_str: str, fmt: str) -> datetime | None:
    """Safely parse date string with error handling."""
    try:
        return datetime.strptime(date_str, fmt)
    except Exception as e:
        logger.error(f"Error parsing date '{date_str}': {e}")
        return None


def get_full_url(url: str) -> str:
    """Convert relative URLs to full NASDAQ URLs."""
    return "https://www.nasdaq.com" + url if url.startswith("/") else url


def fetch_nasdaq_api(url: str) -> dict:
    """
    Fetch data from the Nasdaq API using the provided URL.

    Args:
        url: The API endpoint URL

    Returns:
        dict: JSON response from the API

    Raises:
        requests.RequestException: If the API request fails
    """
    # Refresh cookies if needed
    refresh_nasdaq_cookie()

    response = requests.get(url, headers=_nasdaq_headers.copy())
    response.raise_for_status()
    return response.json()


class NASDAQDataIngestor:
    """Enhanced NASDAQ data ingestion with comprehensive data fetching capabilities."""

    def __init__(self, cookie_manager: NASDAQCookieManager | None = None):
        """
        Initialize NASDAQ data ingestor.

        Args:
            cookie_manager: Optional cookie manager instance
        """
        self.cookie_manager = cookie_manager or NASDAQCookieManager()

    def fetch_company_profile(self, symbol: str) -> str:
        """
        Fetch company description from NASDAQ API.

        Args:
            symbol: Stock symbol

        Returns:
            str: Company description
        """
        try:
            profile_url = f"https://api.nasdaq.com/api/company/{symbol}/company-profile"
            json_data = fetch_nasdaq_api(profile_url)
            data = json_data.get("data", {})
            if data is None:
                return ""
            return data.get("CompanyDescription", {}).get("value", "")
        except Exception as e:
            logger.error(f"Error fetching company profile for {symbol}: {e}")
            return ""

    def fetch_revenue_earnings(self, symbol: str) -> list[dict[str, Any]]:
        """
        Fetch revenue and earnings data for the given stock symbol.

        Args:
            symbol: Stock symbol

        Returns:
            List[Dict]: Revenue and earnings data for last 6 quarters
        """
        try:
            revenue_earnings_url = f"https://api.nasdaq.com/api/company/{symbol}/revenue?limit=1"
            json_data = fetch_nasdaq_api(revenue_earnings_url)
            data = json_data.get("data")
            if not data:
                logger.warning(f"No revenue data found for {symbol}")
                return []

            revenue_table = data.get("revenueTable") or {}
            rows = revenue_table.get("rows") or []

            if not rows:
                logger.warning(f"No rows found in revenue table for {symbol}")
                return []

            # Transpose the table to only include groups containing 4 entries each
            transposed_data = []
            try:
                for i in range(0, len(rows), 4):

                    def safe_convert_value(value):
                        if not value or value == "N/A":
                            return None
                        try:
                            return value.replace("$", "").replace(",", "")
                        except (ValueError, AttributeError):
                            return None

                    quarter_data = {
                        "quarter": rows[i]["value1"],
                        "revenue": safe_convert_value(rows[i + 1]["value2"]),
                        "eps": safe_convert_value(rows[i + 2]["value2"]),
                        "dividends": safe_convert_value(rows[i + 3]["value2"]),
                    }
                    transposed_data.append(quarter_data)
            except Exception as e:
                logger.error(f"Error processing revenue rows for {symbol}: {e}")
                return []

            # Keep only the last 6 quarters
            return transposed_data[-6:]

        except Exception as e:
            logger.error(f"Error fetching revenue/earnings for {symbol}: {e}")
            return []

    def fetch_historical_quotes(
        self, symbol: str, period: int = 5, asset_class: str = "stock"
    ) -> dict[str, dict[str, Any]]:
        """
        Fetch historical prices for the given stock symbol.

        Args:
            symbol: Stock symbol
            period: Number of days of historical data
            asset_class: "stock" or "etf"

        Returns:
            Dict: Historical price data with dates as keys
        """
        try:
            # Calculate dates for the API request
            end_date = datetime.now()
            calendar_days = period * 1.5 if period >= 150 else period
            start_date = end_date - timedelta(days=int(calendar_days))
            asset_class = "stocks" if asset_class == "stock" else "etf"

            historical_url = (
                f"https://api.nasdaq.com/api/quote/{symbol}/historical?"
                f"assetclass={asset_class}&fromdate={start_date.strftime('%Y-%m-%d')}&"
                f"limit={int(calendar_days)}&todate={end_date.strftime('%Y-%m-%d')}"
            )

            json_data = fetch_nasdaq_api(historical_url)
            data = json_data.get("data", {})
            if data is None:
                return {}

            # Extract the trades table
            trades_data = data.get("tradesTable", {}).get("rows") or []

            prices_dict = {}
            for row in trades_data:

                def safe_convert_price(value):
                    if not value or value == "N/A":
                        return None
                    try:
                        return float(value.replace("$", "").replace(",", ""))
                    except (ValueError, AttributeError):
                        return None

                def safe_convert_volume(value):
                    if not value or value == "N/A":
                        return None
                    try:
                        return int(value.replace(",", ""))
                    except (ValueError, AttributeError):
                        return None

                prices_dict[row["date"]] = {
                    "close": safe_convert_price(row.get("close")),
                    "volume": safe_convert_volume(row.get("volume")),
                    "open": safe_convert_price(row.get("open")),
                    "high": safe_convert_price(row.get("high")),
                    "low": safe_convert_price(row.get("low")),
                }

            return prices_dict

        except Exception as e:
            logger.error(f"Error fetching historical quotes for {symbol}: {e}")
            return {}

    def fetch_insider_trading(self, symbol: str) -> dict[str, Any]:
        """
        Fetch insider trading data for the given stock symbol.

        Args:
            symbol: Stock symbol

        Returns:
            Dict: Insider trading information
        """
        try:
            insider_trading_url = (
                f"https://api.nasdaq.com/api/company/{symbol}/insider-trades?"
                f"limit=10&type=all&sortColumn=lastDate&sortOrder=DESC"
            )
            json_data = fetch_nasdaq_api(insider_trading_url)
            data = json_data.get("data", {})
            if data is None:
                return {}

            # Extract relevant information
            number_of_trades = data.get("numberOfTrades", {}).get("rows", [])
            number_of_shares_traded = data.get("numberOfSharesTraded", {}).get("rows", [])
            transaction_table = data.get("transactionTable", {}).get("table", {}).get("rows") or []

            # Remove the "url" field from each transaction
            cleaned_transaction_table = [{k: v for k, v in item.items() if k != "url"} for item in transaction_table]

            return {
                "number_of_trades": number_of_trades,
                "number_of_shares_traded": number_of_shares_traded,
                "transaction_table": cleaned_transaction_table,
            }

        except Exception as e:
            logger.error(f"Error fetching insider trading for {symbol}: {e}")
            return {}

    def fetch_institutional_holdings(self, symbol: str) -> dict[str, Any]:
        """
        Fetch institutional holdings data for the given stock symbol.

        Args:
            symbol: Stock symbol

        Returns:
            Dict: Institutional holdings information
        """
        try:
            institutional_holdings_url = (
                f"https://api.nasdaq.com/api/company/{symbol}/institutional-holdings?"
                f"limit=10&type=TOTAL&sortColumn=marketValue"
            )
            json_data = fetch_nasdaq_api(institutional_holdings_url)
            data = json_data.get("data", {})

            if not data:
                logger.warning(f"No institutional holdings data for {symbol}")
                return {}

            # Extract relevant information using safe nested access
            ownership_summary = safe_get_nested(data, "ownershipSummary", default={})
            active_positions = safe_get_nested(data, "activePositions", "rows", default=[])
            new_sold_out_positions = safe_get_nested(data, "newSoldOutPositions", "rows", default=[])
            holdings_transactions = safe_get_nested(data, "holdingsTransactions", "table", "rows", default=[])

            # Clean holdings transactions by removing URL field
            cleaned_holdings_transactions = [
                {k: v for k, v in item.items() if k != "url"} for item in holdings_transactions
            ]

            return {
                "ownership_summary": ownership_summary,
                "active_positions": active_positions,
                "new_sold_out_positions": new_sold_out_positions,
                "holdings_transactions": cleaned_holdings_transactions,
            }

        except Exception as e:
            logger.error(f"Error fetching institutional holdings for {symbol}: {e}")
            return {}

    def fetch_short_interest(self, symbol: str) -> list[dict[str, Any]]:
        """
        Fetch short interest data for the given stock symbol.

        Args:
            symbol: Stock symbol

        Returns:
            List[Dict]: Short interest data (last 4 entries)
        """
        try:
            short_interest_url = f"https://api.nasdaq.com/api/quote/{symbol}/short-interest?assetClass=stocks"
            json_data = fetch_nasdaq_api(short_interest_url)
            data = json_data.get("data", {})
            if data is None:
                return []

            short_interest_table = data.get("shortInterestTable") or {}
            rows = short_interest_table.get("rows") or []

            # Return only the 4 most recent rows
            return rows[:4]

        except Exception as e:
            logger.error(f"Error fetching short interest for {symbol}: {e}")
            return []

    def fetch_earnings_calendar(self, days_ahead: int = 7) -> pd.DataFrame:
        """
        Fetch earnings calendar for upcoming days.

        Args:
            days_ahead: Number of days to look ahead

        Returns:
            DataFrame: Earnings calendar data
        """
        try:
            all_rows = []

            # Use pandas for date range generation
            date_range = TimeSeriesProcessor.create_earnings_calendar_dates(datetime.now(), days_ahead)

            for current_date in date_range:
                date_str = current_date.strftime("%Y-%m-%d")
                earnings_url = f"https://api.nasdaq.com/api/calendar/earnings?date={date_str}"

                try:
                    json_data = fetch_nasdaq_api(earnings_url)
                except Exception as e:
                    logger.error(f"Error fetching earnings for {date_str}: {e}")
                    continue

                data = json_data.get("data", {})
                if not data:
                    continue

                rows = data.get("rows") or []
                # Add the queried date to each row
                for row in rows:
                    row["callDate"] = date_str
                all_rows.extend(rows)

            df = pd.DataFrame(all_rows)

            if df.empty:
                return df

            try:
                # Use pandas for datetime operations
                df["earnings_date"] = pd.to_datetime(df["callDate"])
                df["days_to_earnings"] = (df["earnings_date"] - pd.Timestamp.now()).dt.days

                # Create the human-readable next_earning_call string
                mapping = [
                    ("callDate", "callDate"),
                    ("lastYearRptDt", "lastYearReportDate"),
                    ("lastYearEPS", "lastYearEPS"),
                    ("time", "reportTime"),
                    ("fiscalQuarterEnding", "fiscalQuarterEnding"),
                    ("epsForecast", "epsForecast"),
                    ("noOfEsts", "numberOfEstimates"),
                ]
                df["next_earning_call"] = df.apply(
                    lambda row: ", ".join(
                        f"{new_key}: {row[old_key]}"
                        for old_key, new_key in mapping
                        if old_key in row and pd.notnull(row[old_key])
                    ),
                    axis=1,
                )

                # Return only the necessary columns
                return df[["symbol", "next_earning_call", "days_to_earnings"]]

            except Exception as e:
                logger.error(f"Error processing earnings data: {e}")
                # In case of errors, still try to return minimal data
                if "callDate" in df.columns and "symbol" in df.columns:
                    df["next_earning_call"] = df.apply(lambda row: f"callDate: {row['callDate']}", axis=1)
                    df["days_to_earnings"] = None
                    return df[["symbol", "next_earning_call", "days_to_earnings"]]
                return pd.DataFrame(columns=["symbol", "next_earning_call", "days_to_earnings"])

        except Exception as e:
            logger.error(f"Error fetching earnings calendar: {e}")
            return pd.DataFrame(columns=["symbol", "next_earning_call", "days_to_earnings"])

    def fetch_nasdaq_screener_data(self) -> pd.DataFrame:
        """
        Fetch both NASDAQ stock and ETF data and combine them.

        Returns:
            DataFrame: Combined stock and ETF data
        """
        try:
            # Fetch stocks data
            stocks_api = "https://api.nasdaq.com/api/screener/stocks?tableonly=false&download=true"
            stocks_json_data = fetch_nasdaq_api(stocks_api)
            stocks_rows = stocks_json_data.get("data", {}).get("rows", [])
            stocks_df = pd.DataFrame(stocks_rows)

            if not stocks_df.empty:
                stocks_df["asset_type"] = "stock"

            # Fetch ETFs data
            etfs_api = "https://api.nasdaq.com/api/screener/etf?tableonly=false&download=true"
            etfs_json_data = fetch_nasdaq_api(etfs_api)
            etfs_rows = etfs_json_data.get("data", {}).get("data", {}).get("rows", [])
            etfs_df = pd.DataFrame(etfs_rows)

            if not etfs_df.empty:
                # Standardize ETF field names to match stocks schema
                field_mapping = {"companyName": "name", "lastSalePrice": "lastsale", "percentageChange": "pctchange"}

                # Rename columns based on mapping
                for old_col, new_col in field_mapping.items():
                    if old_col in etfs_df.columns:
                        etfs_df.rename(columns={old_col: new_col}, inplace=True)

                # Drop unnecessary ETF columns
                columns_to_drop = ["deltaIndicator", "oneYearPercentage"]
                etfs_df = etfs_df.drop(columns=[col for col in columns_to_drop if col in etfs_df.columns])

                # Add missing stock fields as empty strings for ETFs
                missing_fields = ["marketCap", "country", "ipoyear", "volume", "sector", "industry", "url"]
                for field in missing_fields:
                    if field not in etfs_df.columns:
                        etfs_df[field] = ""

                # Mark as ETF
                etfs_df["asset_type"] = "etf"

            # Combine the two dataframes
            combined_df = pd.concat([stocks_df, etfs_df], ignore_index=True)

            # Convert marketCap to numeric for stocks (ignore ETFs with empty marketCap)
            if "marketCap" in combined_df.columns:
                combined_df["marketCap"] = pd.to_numeric(combined_df["marketCap"], errors="coerce")

            return combined_df

        except Exception as e:
            logger.error(f"Error fetching NASDAQ screener data: {e}")
            return pd.DataFrame()

    def fetch_stock_news(self, symbol: str, days_back: int = 7) -> list[str]:
        """
        Fetch recent stock news for the given symbol.

        Args:
            symbol: Stock symbol
            days_back: Number of days to look back for news

        Returns:
            List[str]: List of news items as JSON strings
        """
        try:
            news_url = (
                f"https://www.nasdaq.com/api/news/topic/articlebysymbol?"
                f"q={symbol}|STOCKS&offset=0&limit=5&fallback=true"
            )
            json_data = fetch_nasdaq_api(news_url)
            data = json_data.get("data", {})
            if data is None:
                return []
            rows = data.get("rows", [])

            # Convert to DataFrame for efficient date filtering
            df = pd.DataFrame(rows)
            if df.empty:
                return []

            # Parse dates using pandas
            df["created_date"] = TimeSeriesProcessor.parse_financial_dates(df["created"].tolist(), ["%b %d, %Y"])

            # Filter recent news using pandas
            df_recent = TimeSeriesProcessor.filter_recent_data(df, "created_date", days_back)

            recent_news = []
            for _, row in df_recent.iterrows():
                news_url_field = row.get("url", "")
                full_url = get_full_url(news_url_field)
                news_item = {
                    "title": row.get("title", ""),
                    "created": row.get("created", ""),
                    "publisher": row.get("publisher", ""),
                    "url": full_url,
                }
                recent_news.append(json.dumps(news_item))

            return recent_news

        except Exception as e:
            logger.error(f"Error fetching stock news for {symbol}: {e}")
            return []

    def fetch_press_releases(self, symbol: str, days_back: int = 15) -> list[str]:
        """
        Fetch recent press releases for the given symbol.

        Args:
            symbol: Stock symbol
            days_back: Number of days to look back for press releases

        Returns:
            List[str]: List of press releases as JSON strings
        """
        try:
            url = (
                f"https://www.nasdaq.com/api/news/topic/press_release?"
                f"q=symbol:{symbol}|assetclass:stocks&limit=10&offset=0"
            )
            json_data = fetch_nasdaq_api(url)
            data = json_data.get("data", {})
            if data is None:
                return []
            rows = data.get("rows") or []

            recent_releases = []
            cutoff_date = datetime.now() - timedelta(days=days_back)

            for row in rows:
                created_date = safe_parse_date(row["created"], "%b %d, %Y")
                if not created_date or created_date < cutoff_date:
                    continue

                pr_url = row.get("url", "")
                full_url = get_full_url(pr_url)
                press_release = {
                    "title": row.get("title", ""),
                    "created": row.get("created", ""),
                    "publisher": row.get("publisher", ""),
                    "url": full_url,
                }
                recent_releases.append(json.dumps(press_release))

            return recent_releases

        except Exception as e:
            logger.error(f"Error fetching press releases for {symbol}: {e}")
            return []


# Example usage and testing
if __name__ == "__main__":
    # Logging is configured centrally by the pipeline runner.

    # Test cookie refresh
    manager = NASDAQCookieManager()
    success = manager.refresh_cookies()

    if success:
        headers = manager.get_headers()
        print("✅ NASDAQ cookies refreshed successfully")
        print(f"Headers include {len(headers)} items")
        if "cookie" in headers:
            cookie_count = len(headers["cookie"].split(";"))
            print(f"Cookie header contains {cookie_count} cookies")

        # Test the enhanced data ingestor
        ingestor = NASDAQDataIngestor(manager)

        # Test company profile
        profile = ingestor.fetch_company_profile("AAPL")
        print(f"✅ Company profile fetched: {len(profile)} characters")

        # Test revenue/earnings
        revenue_data = ingestor.fetch_revenue_earnings("AAPL")
        print(f"✅ Revenue data fetched: {len(revenue_data)} quarters")

        # Test historical quotes
        historical_data = ingestor.fetch_historical_quotes("AAPL", period=30)
        print(f"✅ Historical data fetched: {len(historical_data)} days")

    else:
        print("❌ Failed to refresh NASDAQ cookies")

