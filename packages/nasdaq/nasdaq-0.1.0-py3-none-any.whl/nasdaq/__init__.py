"""
NASDAQ Public API Client.

A minimal Python client for accessing NASDAQ's public API with automated
cookie management and data retrieval capabilities.
"""

__version__ = "0.1.0"
__author__ = "r-bit-rry"
__email__ = "34023431+r-bit-rry@users.noreply.github.com"
__license__ = "MIT"
__copyright__ = "Copyright 2025, r-bit-rry"

from .data_processing import DataProcessing
from .data_processing import FinancialDataProcessor
from .data_processing import LargeDatasetProcessor
from .data_processing import TimeSeriesProcessor
from .nasdaq import NASDAQCookieManager
from .nasdaq import NASDAQDataIngestor
from .nasdaq import get_nasdaq_headers
from .nasdaq import refresh_nasdaq_cookie


__all__ = [
    "DataProcessing",
    "FinancialDataProcessor",
    "LargeDatasetProcessor",
    "NASDAQCookieManager",
    "NASDAQDataIngestor",
    "TimeSeriesProcessor",
    "get_nasdaq_headers",
    "refresh_nasdaq_cookie",
]

