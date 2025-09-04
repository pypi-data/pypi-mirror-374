"""
Enhanced data processing utilities with pandas optimization.

This module provides unified data processing utilities that leverage pandas
for all operations with memory optimization techniques for large datasets,
replacing custom time series operations throughout the ingestion modules.
"""

import logging
from datetime import date
from datetime import datetime
from datetime import timedelta
from typing import Any

import numpy as np
import pandas as pd


logger = logging.getLogger(__name__)


class DataProcessing:
    """
    Unified data processing utilities with pandas backend.

    Provides optimized time series operations, data alignment, and aggregation
    functions that replace custom implementations in ingestion modules.
    """

    @staticmethod
    def create_date_range(
        start_date: date | datetime | str, end_date: date | datetime | str, freq: str = "D"
    ) -> pd.DatetimeIndex:
        """
        Create a pandas date range, replacing manual date iteration.

        Args:
            start_date: Start date
            end_date: End date
            freq: Frequency string ('D' for daily, 'B' for business days, etc.)

        Returns:
            pd.DatetimeIndex: Date range
        """
        return pd.date_range(start=start_date, end=end_date, freq=freq)

    @staticmethod
    def _ta_to_series(index: pd.Index, values: np.ndarray) -> pd.Series:
        """Helper to convert TA-Lib numpy output to pandas Series with original index."""
        return pd.Series(values, index=index)

    @staticmethod
    def calculate_days_between(
        start_dates: pd.Series | list[date] | list[datetime], end_dates: pd.Series | list[date] | list[datetime]
    ) -> pd.Series:
        """
        Calculate days between dates using pandas vectorized operations.

        Replaces manual timedelta calculations in loops.

        Args:
            start_dates: Start dates
            end_dates: End dates

        Returns:
            pd.Series: Days between dates (integer values, NaN for invalid dates)

        Raises:
            ValueError: If input arrays have different lengths
        """
        # Convert to datetime with error handling and ensure Series output
        start_series = pd.Series(pd.to_datetime(start_dates, errors="coerce"))
        end_series = pd.Series(pd.to_datetime(end_dates, errors="coerce"))

        # Validate lengths match
        if len(start_series) != len(end_series):
            raise ValueError(f"Input arrays must have same length: {len(start_series)} vs {len(end_series)}")

        # Calculate difference and extract days
        timedelta_diff = end_series - start_series
        return timedelta_diff.dt.days

    @staticmethod
    def filter_by_date_range(
        df: pd.DataFrame,
        date_column: str,
        start_date: date | datetime | str | None = None,
        end_date: date | datetime | str | None = None,
    ) -> pd.DataFrame:
        """
        Filter DataFrame by date range using pandas boolean indexing.

        Replaces manual date filtering loops in ingestion modules.

        Args:
            df: DataFrame to filter
            date_column: Name of date column
            start_date: Start date (optional)
            end_date: End date (optional)

        Returns:
            pd.DataFrame: Filtered DataFrame
        """
        if df.empty:
            return df

        # Ensure date column is datetime
        df = df.copy()
        df[date_column] = pd.to_datetime(df[date_column])

        # Apply filters
        mask = pd.Series(True, index=df.index)

        if start_date is not None:
            start_date = pd.to_datetime(start_date)
            mask &= df[date_column] >= start_date

        if end_date is not None:
            end_date = pd.to_datetime(end_date)
            mask &= df[date_column] <= end_date

        return df[mask]

    @staticmethod
    def align_time_series(
        data_list: list[pd.DataFrame], date_column: str = "date", method: str = "outer"
    ) -> pd.DataFrame:
        """
        Align multiple time series DataFrames on dates.

        Args:
            data_list: List of DataFrames to align
            date_column: Name of date column
            method: Join method ('outer', 'inner', 'left', 'right')

        Returns:
            pd.DataFrame: Aligned time series data
        """
        if not data_list:
            return pd.DataFrame()

        if len(data_list) == 1:
            return data_list[0].copy()

        # Set date as index for all DataFrames
        aligned_dfs = []
        for i, df in enumerate(data_list):
            df_copy = df.copy()
            df_copy[date_column] = pd.to_datetime(df_copy[date_column])
            df_copy = df_copy.set_index(date_column)

            # Add suffix to avoid column name conflicts
            if i > 0:
                df_copy = df_copy.add_suffix(f"_{i}")

            aligned_dfs.append(df_copy)

        # Align using pandas join
        result = aligned_dfs[0]
        for df in aligned_dfs[1:]:
            result = result.join(df, how=method)

        return result.reset_index()

    @staticmethod
    def calculate_rolling_metrics(data: pd.Series, window: int, metrics: list[str] | None = None) -> pd.DataFrame:
        """
        Calculate rolling window metrics using pandas.

        Args:
            data: Time series data
            window: Rolling window size
            metrics: List of metrics to calculate

        Returns:
            pd.DataFrame: Rolling metrics
        """
        if metrics is None:
            metrics = ["mean", "std", "min", "max"]
        rolling = data.rolling(window=window)

        result = pd.DataFrame(index=data.index)

        for metric in metrics:
            if hasattr(rolling, metric):
                result[f"rolling_{metric}_{window}"] = getattr(rolling, metric)()
            else:
                logger.warning(f"Unknown rolling metric: {metric}")

        return result

    @staticmethod
    def handle_missing_data(
        df: pd.DataFrame, strategy: str = "interpolate", columns: list[str] | None = None
    ) -> pd.DataFrame:
        """
        Handle missing data using pandas methods.

        Args:
            df: DataFrame with missing data
            strategy: Strategy ('interpolate', 'forward_fill', 'backward_fill', 'drop')
            columns: Columns to process (None for all)

        Returns:
            pd.DataFrame: DataFrame with missing data handled
        """
        df_copy = df.copy()

        if columns is None:
            columns = df_copy.select_dtypes(include=[np.number]).columns.tolist()

        for col in columns:
            if col not in df_copy.columns:
                continue

            if strategy == "interpolate":
                df_copy[col] = df_copy[col].interpolate()
            elif strategy == "forward_fill":
                df_copy[col] = df_copy[col].ffill()
            elif strategy == "backward_fill":
                df_copy[col] = df_copy[col].bfill()
            elif strategy == "drop":
                df_copy = df_copy.dropna(subset=[col])
            else:
                logger.warning(f"Unknown missing data strategy: {strategy}")

        return df_copy

    @staticmethod
    def aggregate_by_period(
        df: pd.DataFrame, date_column: str, value_columns: list[str], period: str = "M", agg_func: str = "mean"
    ) -> pd.DataFrame:
        """
        Aggregate data by time period using pandas groupby.

        Args:
            df: DataFrame to aggregate
            date_column: Date column name
            value_columns: Columns to aggregate
            period: Period ('D', 'W', 'M', 'Q', 'Y')
            agg_func: Aggregation function

        Returns:
            pd.DataFrame: Aggregated data
        """
        df_copy = df.copy()
        df_copy[date_column] = pd.to_datetime(df_copy[date_column])

        # Create period grouper
        grouper = pd.Grouper(key=date_column, freq=period)

        # Aggregate
        agg_dict = {col: agg_func for col in value_columns}
        result = df_copy.groupby(grouper).agg(agg_dict).reset_index()

        return result

    @staticmethod
    def optimize_memory_usage(df: pd.DataFrame) -> pd.DataFrame:
        """
        Optimize DataFrame memory usage using pandas techniques.

        Args:
            df: DataFrame to optimize

        Returns:
            pd.DataFrame: Memory-optimized DataFrame
        """
        df_optimized = df.copy()

        # Optimize numeric columns
        for col in df_optimized.select_dtypes(include=["int64"]).columns:
            df_optimized[col] = pd.to_numeric(df_optimized[col], downcast="integer")

        for col in df_optimized.select_dtypes(include=["float64"]).columns:
            df_optimized[col] = pd.to_numeric(df_optimized[col], downcast="float")

        # Optimize object columns
        for col in df_optimized.select_dtypes(include=["object"]).columns:
            if df_optimized[col].nunique() / len(df_optimized) < 0.5:
                df_optimized[col] = df_optimized[col].astype("category")

        return df_optimized


class FinancialDataProcessor:
    """
    Specialized financial data processing utilities.

    Provides pandas-based aggregation functions that replace custom
    financial data manipulation throughout the system.
    """

    @staticmethod
    def aggregate_adjustments(adjustments: list[Any], group_by: str = "adjustment_type") -> pd.DataFrame:
        """
        Aggregate financial adjustments using pandas groupby.

        Replaces manual aggregation loops in adjustment_engine.py.

        Args:
            adjustments: List of adjustment objects
            group_by: Field to group by

        Returns:
            pd.DataFrame: Aggregated adjustment statistics
        """
        if not adjustments:
            return pd.DataFrame()

        # Convert to DataFrame
        data = []
        for adj in adjustments:
            data.append(
                {
                    "adjustment_type": getattr(adj, "adjustment_type", "unknown"),
                    "amount": getattr(adj, "amount", 0.0),
                    "confidence": getattr(adj, "confidence", 0.0),
                    "period": getattr(adj, "period", None),
                }
            )

        df = pd.DataFrame(data)

        # Aggregate using pandas groupby
        result = (
            df.groupby(group_by)
            .agg({"amount": ["count", "sum", "mean", "std"], "confidence": ["mean", "min", "max"]})
            .round(4)
        )

        # Flatten column names
        result.columns = ["_".join(col).strip() for col in result.columns]

        return result.reset_index()

    @staticmethod
    def aggregate_cash_flows(cash_flows: list[Any], metrics: list[str] | None = None) -> dict[str, float]:
        """
        Aggregate cash flow data using pandas.

        Replaces manual sum calculations in capital_budgeting.py.

        Args:
            cash_flows: List of cash flow objects
            metrics: Metrics to aggregate

        Returns:
            Dict[str, float]: Aggregated metrics
        """
        if metrics is None:
            metrics = ["revenue", "expenses", "depreciation", "tax"]
        if not cash_flows:
            return {f"total_{metric}": 0.0 for metric in metrics}

        # Convert to DataFrame
        data = []
        for cf in cash_flows:
            row = {}
            for metric in metrics:
                if metric == "expenses":
                    # Handle combined expenses
                    variable = getattr(cf, "variable_expenses", 0.0)
                    fixed = getattr(cf, "fixed_expenses", 0.0)
                    row[metric] = variable + fixed
                else:
                    row[metric] = getattr(cf, metric, 0.0)
            data.append(row)

        df = pd.DataFrame(data)

        # Calculate aggregations
        result = {}
        for metric in metrics:
            if metric in df.columns:
                result[f"total_{metric}"] = df[metric].sum()
                result[f"avg_{metric}"] = df[metric].mean()
                result[f"max_{metric}"] = df[metric].max()
                result[f"min_{metric}"] = df[metric].min()

        return result

    @staticmethod
    def aggregate_validation_metrics(periods: list[Any], metrics: list[str] | None = None) -> dict[str, float]:
        """
        Aggregate validation metrics using pandas.

        Replaces manual calculations in validation modules.

        Args:
            periods: List of period objects
            metrics: Metrics to aggregate

        Returns:
            Dict[str, float]: Aggregated validation metrics
        """
        if metrics is None:
            metrics = ["data_completeness", "confidence_score", "csr_compliance"]
        if not periods:
            return {f"avg_{metric}": 0.0 for metric in metrics}

        # Convert to DataFrame
        data = []
        for period in periods:
            row = {}
            for metric in metrics:
                if metric == "csr_compliance":
                    # Convert boolean to numeric
                    row[metric] = float(getattr(period, metric, False))
                else:
                    row[metric] = getattr(period, metric, 0.0)
            data.append(row)

        df = pd.DataFrame(data)

        # Calculate aggregations
        result = {}
        for metric in metrics:
            if metric in df.columns:
                result[f"avg_{metric}"] = df[metric].mean()
                result[f"std_{metric}"] = df[metric].std()
                result[f"min_{metric}"] = df[metric].min()
                result[f"max_{metric}"] = df[metric].max()

                if metric == "csr_compliance":
                    result["compliance_score"] = df[metric].mean()
                    result["compliant_periods"] = df[metric].sum()

        return result

    @staticmethod
    def aggregate_market_data(
        market_data: list[dict[str, Any]], group_by: str = "ticker", agg_functions: dict[str, str] | None = None
    ) -> pd.DataFrame:
        """
        Aggregate market data using pandas groupby.

        Args:
            market_data: List of market data dictionaries
            group_by: Column to group by
            agg_functions: Custom aggregation functions

        Returns:
            pd.DataFrame: Aggregated market data
        """
        if not market_data:
            return pd.DataFrame()

        df = pd.DataFrame(market_data)

        if agg_functions is None:
            agg_functions = {"adjusted_close": "last", "volume": "sum", "date": "max"}

        # Filter columns that exist in the DataFrame
        valid_agg = {k: v for k, v in agg_functions.items() if k in df.columns}

        if group_by in df.columns and valid_agg:
            return df.groupby(group_by).agg(valid_agg).reset_index()

        return df

    @staticmethod
    def merge_financial_datasets(
        datasets: list[pd.DataFrame], on: str | list[str], how: str = "outer", suffixes: list[str] | None = None
    ) -> pd.DataFrame:
        """
        Merge multiple financial datasets using pandas.

        Args:
            datasets: List of DataFrames to merge
            on: Column(s) to merge on
            how: Type of merge
            suffixes: Suffixes for overlapping columns

        Returns:
            pd.DataFrame: Merged DataFrame
        """
        if not datasets:
            return pd.DataFrame()

        if len(datasets) == 1:
            return datasets[0].copy()

        result = datasets[0]

        for i, df in enumerate(datasets[1:], 1):
            suffix_pair = ("", f"_{i}") if suffixes is None else ("", suffixes[i - 1])
            result = pd.merge(result, df, on=on, how=how, suffixes=suffix_pair)

        return result


class TimeSeriesProcessor:
    """
    Specialized time series processing for financial data.

    Replaces custom time series operations in ingestion modules with
    optimized pandas operations.
    """

    @staticmethod
    def parse_financial_dates(date_strings: list[str], formats: list[str] | None = None) -> pd.Series:
        """
        Parse financial date strings using pandas with multiple format support.

        Replaces manual date parsing loops in ingestion modules.

        Args:
            date_strings: List of date strings
            formats: List of date formats to try

        Returns:
            pd.Series: Parsed dates
        """
        if formats is None:
            formats = ["%m/%d/%Y", "%Y-%m-%d", "%b %d, %Y"]
        dates = pd.Series(date_strings)

        for fmt in formats:
            try:
                parsed = pd.to_datetime(dates, format=fmt, errors="coerce")
                # If we got some valid dates, use this format
                if parsed.notna().any():
                    # For remaining NaT values, try next format
                    mask = parsed.isna()
                    if mask.any():
                        continue
                    return parsed
            except Exception:
                continue

        # Fallback to pandas automatic parsing
        try:
            return pd.to_datetime(dates, errors="coerce")
        except Exception:
            logger.warning("Failed to parse some dates, returning NaT for failed entries")
            return pd.Series([pd.NaT] * len(date_strings))

    @staticmethod
    def create_earnings_calendar_dates(base_date: datetime, days_ahead: int) -> pd.DatetimeIndex:
        """
        Create date range for earnings calendar using pandas.

        Replaces manual date iteration in nasdaq.py.

        Args:
            base_date: Base date
            days_ahead: Number of days ahead

        Returns:
            pd.DatetimeIndex: Date range
        """
        return pd.date_range(start=base_date, periods=days_ahead, freq="D")

    @staticmethod
    def filter_recent_data(
        df: pd.DataFrame, date_column: str, days_back: int, reference_date: datetime | None = None
    ) -> pd.DataFrame:
        """
        Filter DataFrame for recent data using pandas.

        Replaces manual date filtering in news/press release functions.

        Args:
            df: DataFrame to filter
            date_column: Date column name
            days_back: Number of days to look back
            reference_date: Reference date (defaults to now)

        Returns:
            pd.DataFrame: Filtered DataFrame
        """
        if reference_date is None:
            reference_date = datetime.now()

        cutoff_date = reference_date - timedelta(days=days_back)

        df_copy = df.copy()
        df_copy[date_column] = pd.to_datetime(df_copy[date_column])

        return df_copy[df_copy[date_column] >= cutoff_date]

    @staticmethod
    def calculate_period_returns(prices: pd.Series, periods: list[int] | None = None) -> pd.DataFrame:
        """
        Calculate returns for multiple periods using pandas.

        Args:
            prices: Price series
            periods: List of periods for return calculation

        Returns:
            pd.DataFrame: Returns for different periods
        """
        if periods is None:
            periods = [1, 5, 10, 20, 60, 252]
        result = pd.DataFrame(index=prices.index)

        for period in periods:
            result[f"return_{period}d"] = prices.pct_change(periods=period)

        return result

    @staticmethod
    def resample_financial_data(
        df: pd.DataFrame, date_column: str, freq: str, agg_methods: dict[str, str]
    ) -> pd.DataFrame:
        """
        Resample financial data to different frequencies.

        Args:
            df: DataFrame to resample
            date_column: Date column name
            freq: Target frequency ('D', 'W', 'M', 'Q')
            agg_methods: Dictionary mapping columns to aggregation methods

        Returns:
            pd.DataFrame: Resampled data
        """
        df_copy = df.copy()
        df_copy[date_column] = pd.to_datetime(df_copy[date_column])
        df_copy = df_copy.set_index(date_column)

        return df_copy.resample(freq).agg(agg_methods).reset_index()


class LargeDatasetProcessor:
    """
    Optimized data processing for large datasets using pandas techniques.

    Provides memory-efficient alternatives for processing large datasets.
    """

    @staticmethod
    def process_large_market_data(data: list[dict[str, Any]], operations: list[str] | None = None) -> pd.DataFrame:
        """
        Process large market data using optimized pandas operations.

        Args:
            data: List of market data dictionaries
            operations: List of operations to perform

        Returns:
            pd.DataFrame: Processed data
        """
        if operations is None:
            operations = ["sort", "deduplicate", "aggregate"]
        df = pd.DataFrame(data)

        # Optimize memory usage first
        df = DataProcessing.optimize_memory_usage(df)

        if "sort" in operations:
            df = df.sort_values(["ticker", "date"] if "ticker" in df.columns else df.columns[0])

        if "deduplicate" in operations:
            df = df.drop_duplicates(["ticker", "date"] if "ticker" in df.columns else None)

        if "aggregate" in operations and "ticker" in df.columns:
            df = df.groupby("ticker").agg({"adjusted_close": "last", "volume": "sum"}).reset_index()

        return df

    @staticmethod
    def benchmark_operations(df: pd.DataFrame, operation: str = "groupby") -> dict[str, float]:
        """
        Benchmark pandas operations for performance monitoring.

        Args:
            df: Test DataFrame
            operation: Operation to benchmark

        Returns:
            Dict[str, float]: Timing results
        """
        import time

        results = {}

        # Standard pandas operation
        start_time = time.time()
        if operation == "groupby" and "ticker" in df.columns:
            _ = df.groupby("ticker").agg({"adjusted_close": "mean"})
        elif operation == "sort":
            _ = df.sort_values(["ticker", "date"] if "ticker" in df.columns else df.columns[0])
        standard_time = time.time() - start_time
        results["standard_pandas"] = standard_time

        # Memory-optimized pandas operation
        df_optimized = DataProcessing.optimize_memory_usage(df)
        start_time = time.time()
        if operation == "groupby" and "ticker" in df_optimized.columns:
            _ = df_optimized.groupby("ticker").agg({"adjusted_close": "mean"})
        elif operation == "sort":
            _ = df_optimized.sort_values(
                ["ticker", "date"] if "ticker" in df_optimized.columns else df_optimized.columns[0]
            )
        optimized_time = time.time() - start_time
        results["optimized_pandas"] = optimized_time

        if optimized_time > 0:
            results["improvement_factor"] = standard_time / optimized_time

        return results


# Convenience functions for backward compatibility
def create_date_range(start_date, end_date, freq="D"):
    """Convenience function for date range creation."""
    return DataProcessing.create_date_range(start_date, end_date, freq)


def filter_by_date_range(df, date_column, start_date=None, end_date=None):
    """Convenience function for date filtering."""
    return DataProcessing.filter_by_date_range(df, date_column, start_date, end_date)


def parse_financial_dates(date_strings, formats=None):
    """Convenience function for date parsing."""
    if formats is None:
        formats = ["%m/%d/%Y", "%Y-%m-%d", "%b %d, %Y"]
    return TimeSeriesProcessor.parse_financial_dates(date_strings, formats)


def optimize_dataframe_memory(df):
    """Convenience function for memory optimization."""
    return DataProcessing.optimize_memory_usage(df)


def process_large_dataset_chunked(df, chunk_size=10000, operation=None):
    """Convenience function for chunked processing."""
    return DataProcessing.process_large_dataset_chunked(df, chunk_size, operation)
