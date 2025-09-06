"""
Parameterized Polars Analytics Utility

Provides highly configurable data analysis functions that sales agents can use
with different parameters to perform various types of statistical analysis.
"""

from typing import Dict, List, Any, Optional, Union, Tuple
import re
import json
from datetime import datetime
from enum import Enum
from utils.lazy_load import get_polars, get_numpy, get_scipy_stats, get_pandas


class AnalysisType(Enum):
    """Available analysis types (restricted to core four)"""

    # Core categories
    OVERVIEW = "overview"  # Comprehensive summary (descriptive + distribution + basic insights)
    PERFORMANCE = "performance"  # Rankings, comparisons, outliers, performance gaps
    TRENDS = "trends"  # Temporal analysis, forecasting, seasonality
    RELATIONSHIPS = "relationships"  # Correlations, regression, dependencies


class AggregationMethod(Enum):
    """Available aggregation methods"""

    SUM = "sum"
    MEAN = "mean"
    MEDIAN = "median"
    COUNT = "count"
    MIN = "min"
    MAX = "max"
    STD = "std"
    VAR = "var"
    QUANTILE = "quantile"


def parse_tabular_data(data: str):
    """
    Parse various tabular data formats into Polars DataFrame with comprehensive error handling

    Args:
        data: Raw string data in table format

    Returns:
        Polars DataFrame or None if parsing fails
    """
    if not data or not isinstance(data, str):
        return None

    try:
        # Log data characteristics for debugging
        data_length = len(data)
        data_lines = data.count("\n") + 1
        has_pipes = "|" in data
        has_separators = "---" in data or ":-:" in data
        has_commas = "," in data
        has_json = "{" in data and "}" in data

        from utils.logger import logger

        logger.debug(
            f"Parsing tabular data: length={data_length}, lines={data_lines}, pipes={has_pipes}, separators={has_separators}, commas={has_commas}, json={has_json}"
        )

        # Try markdown format first (most common in our case)
        if has_pipes and (has_separators or "sum(" in data.lower()):
            logger.debug("Attempting markdown table parsing...")
            result = _parse_markdown_table(data)
            if result is not None:
                logger.debug(
                    f"Markdown parsing successful: {result.shape[0]}x{result.shape[1]} DataFrame"
                )
                return result
            logger.debug("Markdown parsing failed, trying other formats...")

        # Try CSV format
        if has_commas and data_lines > 1:
            logger.debug("Attempting CSV parsing...")
            result = _parse_csv_format(data)
            if result is not None:
                logger.debug(
                    f"CSV parsing successful: {result.shape[0]}x{result.shape[1]} DataFrame"
                )
                return result
            logger.debug("CSV parsing failed, trying other formats...")

        # Try JSON format
        if has_json:
            logger.debug("Attempting JSON parsing...")
            result = _parse_json_format(data)
            if result is not None:
                logger.debug(
                    f"JSON parsing successful: {result.shape[0]}x{result.shape[1]} DataFrame"
                )
                return result
            logger.debug("JSON parsing failed")

        # If all specific formats fail, try a more flexible approach
        logger.debug("All standard parsers failed, attempting flexible parsing...")
        return _flexible_table_parser(data)

    except Exception as e:
        from utils.logger import logger

        logger.error(f"Unexpected error in parse_tabular_data: {str(e)}")
        return None


def analyze_data(
    df,
    analysis_type: str,
    target_columns: Optional[List[str]] = None,
    group_by_columns: Optional[List[str]] = None,
    time_column: Optional[str] = None,
    aggregation_method: str = "sum",
    percentiles: List[float] = [0.25, 0.5, 0.75],
    window_size: int = 3,
    correlation_threshold: float = 0.3,
    outlier_method: str = "iqr",
    outlier_threshold: float = 1.5,
    trend_periods: int = 5,
    statistical_tests: bool = False,
    confidence_level: float = 0.95,
    **kwargs,
) -> Dict[str, Any]:
    """
    Perform parameterized data analysis

    Args:
        df: Polars DataFrame to analyze
        analysis_type: Type of analysis (descriptive, comparative, temporal, etc.)
        target_columns: Specific columns to analyze (None for all numeric)
        group_by_columns: Columns to group by for comparative analysis
        time_column: Column to use for temporal analysis
        aggregation_method: Method for aggregating data
        percentiles: Percentiles to calculate
        window_size: Window size for moving averages/rolling calculations
        correlation_threshold: Minimum correlation strength to report
        outlier_method: Method for outlier detection (iqr, zscore, modified_zscore)
        outlier_threshold: Threshold for outlier detection
        trend_periods: Number of periods to analyze for trends
        statistical_tests: Whether to perform statistical significance tests
        confidence_level: Confidence level for statistical tests
        **kwargs: Additional parameters for specific analyses

    Returns:
        Dictionary with analysis results
    """

    # Validate and prepare data
    if df.height == 0:
        return {"error": "DataFrame is empty"}

    # Auto-detect column types if not specified
    pl = get_polars()
    numeric_cols = [
        col
        for col in df.columns
        if df[col].dtype in [pl.Int64, pl.Float64, pl.Int32, pl.Float32]
    ]
    categorical_cols = [col for col in df.columns if df[col].dtype == pl.Utf8]
    date_cols = [col for col in df.columns if df[col].dtype in [pl.Date, pl.Datetime]]

    # Use specified columns or auto-detect
    target_columns = target_columns or numeric_cols
    target_columns = [col for col in target_columns if col in df.columns]

    results = {
        "analysis_type": analysis_type,
        "parameters": {
            "target_columns": target_columns,
            "group_by_columns": group_by_columns,
            "aggregation_method": aggregation_method,
            "window_size": window_size,
            "time_column": time_column,
            "trend_periods": trend_periods,
        },
        "data_info": {
            "shape": {"rows": df.height, "columns": df.width},
            "column_types": {
                "numeric": numeric_cols,
                "categorical": categorical_cols,
                "date": date_cols,
            },
        },
        "timestamp": datetime.now().isoformat(),
    }

    try:
        # Route to specific analysis function - NEW SIMPLIFIED TYPES FIRST
        if analysis_type == AnalysisType.OVERVIEW.value:
            results["analysis"] = _overview_analysis(
                df, target_columns, percentiles, statistical_tests, confidence_level
            )

        elif analysis_type == AnalysisType.PERFORMANCE.value:
            results["analysis"] = _performance_analysis(
                df,
                target_columns,
                group_by_columns,
                aggregation_method,
                outlier_method,
                outlier_threshold,
                **kwargs,
            )

        elif analysis_type == AnalysisType.TRENDS.value:
            results["analysis"] = _trends_analysis(
                df,
                target_columns,
                group_by_columns,
                time_column,
                window_size,
                trend_periods,
                aggregation_method,
            )

        elif analysis_type == AnalysisType.RELATIONSHIPS.value:
            results["analysis"] = _relationships_analysis(
                df, target_columns, correlation_threshold, **kwargs
            )

        else:
            # Invalid analysis type
            results["error"] = (
                f"Invalid analysis type: {analysis_type}. Allowed: overview, performance, trends, relationships"
            )
            return results

        # Add insights and recommendations
        results["insights"] = _generate_insights(df, results["analysis"], analysis_type)
        results["recommendations"] = _generate_recommendations(
            df, results["analysis"], analysis_type
        )

        return results

    except Exception as e:
        results["error"] = f"Analysis failed: {str(e)}"
        return results


def _descriptive_analysis(
    df,
    target_columns: List[str],
    percentiles: List[float],
    statistical_tests: bool,
    confidence_level: float,
) -> Dict[str, Any]:
    """Perform descriptive statistical analysis"""

    results = {}

    for col in target_columns:
        if col not in df.columns:
            continue

        # Basic descriptive statistics
        pl = get_polars()
        basic_stats = df.select(
            [
                pl.col(col).count().alias("count"),
                pl.col(col).sum().alias("sum"),
                pl.col(col).mean().alias("mean"),
                pl.col(col).median().alias("median"),
                pl.col(col).std(ddof=1).alias("std"),
                pl.col(col).var(ddof=1).alias("variance"),
                pl.col(col).min().alias("min"),
                pl.col(col).max().alias("max"),
                # Quartiles
                pl.col(col).quantile(0.25).alias("q1"),
                pl.col(col).quantile(0.75).alias("q3"),
            ]
        ).to_dicts()[0]

        # Calculate mode (most frequent value)
        try:
            mode_result = df.select(
                pl.col(col)
                .drop_nulls()
                .value_counts()
                .sort("counts", descending=True)
                .first()
            ).to_dicts()

            if mode_result and len(mode_result) > 0 and mode_result[0] is not None:
                mode_data = mode_result[0][col]
                if isinstance(mode_data, dict) and col in mode_data:
                    basic_stats["mode"] = mode_data[col]
                    basic_stats["mode_frequency"] = mode_data.get("counts", 0)
                else:
                    # Fallback: get most frequent value directly
                    value_counts = (
                        df[col]
                        .drop_nulls()
                        .value_counts()
                        .sort("counts", descending=True)
                    )
                    if value_counts.height > 0:
                        top_value = value_counts.row(0)
                        basic_stats["mode"] = top_value[0]
                        basic_stats["mode_frequency"] = top_value[1]
                    else:
                        basic_stats["mode"] = None
                        basic_stats["mode_frequency"] = 0
            else:
                basic_stats["mode"] = None
                basic_stats["mode_frequency"] = 0
        except Exception:
            basic_stats["mode"] = None
            basic_stats["mode_frequency"] = 0

        # Calculate skewness and kurtosis using scipy with robust handling
        col_values = df[col].drop_nulls().to_list()
        if (
            col_values and len(col_values) > 2
        ):  # Need at least 3 values for meaningful skewness/kurtosis
            # Check for low variability to avoid precision warnings
            col_std = basic_stats.get("std", 0)
            col_mean = basic_stats.get("mean", 0)

            # If coefficient of variation is very low, the data is nearly identical
            cv_threshold = 1e-10  # Very small threshold for numerical stability
            if col_std and col_mean and abs(col_std / col_mean) > cv_threshold:
                try:
                    import warnings

                    # Temporarily suppress precision warnings for this calculation
                    with warnings.catch_warnings():
                        warnings.filterwarnings(
                            "ignore",
                            category=RuntimeWarning,
                            message=".*Precision loss.*catastrophic cancellation.*",
                        )
                        skew_val = get_scipy_stats().skew(col_values)
                        kurt_val = get_scipy_stats().kurtosis(col_values)

                        # Check if results are valid numbers
                        basic_stats["skewness"] = (
                            float(skew_val)
                            if not (
                                get_numpy().isnan(skew_val)
                                or get_numpy().isinf(skew_val)
                            )
                            else 0.0
                        )
                        basic_stats["kurtosis"] = (
                            float(kurt_val)
                            if not (
                                get_numpy().isnan(kurt_val)
                                or get_numpy().isinf(kurt_val)
                            )
                            else 0.0
                        )
                except (RuntimeWarning, FloatingPointError, ValueError):
                    # If calculation fails, set to neutral values
                    basic_stats["skewness"] = 0.0
                    basic_stats["kurtosis"] = 0.0
            else:
                # Data has very low variability, skewness and kurtosis are not meaningful
                basic_stats["skewness"] = 0.0
                basic_stats["kurtosis"] = 0.0
        else:
            # Not enough data points for meaningful calculation
            basic_stats["skewness"] = 0.0
            basic_stats["kurtosis"] = 0.0

        col_stats = basic_stats

        # Calculate specified percentiles
        percentile_results = {}
        for p in percentiles:
            percentile_val = df[col].quantile(p)
            percentile_results[f"p{int(p * 100)}"] = (
                float(percentile_val) if percentile_val else None
            )

        col_stats["percentiles"] = percentile_results

        # Additional derived statistics
        if col_stats["mean"] and col_stats["mean"] != 0:
            col_stats["coefficient_of_variation"] = col_stats["std"] / col_stats["mean"]

        col_stats["range"] = col_stats["max"] - col_stats["min"]
        col_stats["iqr"] = percentile_results.get("p75", 0) - percentile_results.get(
            "p25", 0
        )

        # Null handling
        col_stats["null_count"] = df[col].null_count()
        col_stats["null_percentage"] = (col_stats["null_count"] / df.height) * 100

        # Statistical tests if requested
        if statistical_tests:
            col_stats["confidence_intervals"] = _calculate_confidence_intervals(
                df[col], confidence_level
            )
            col_stats["normality_test"] = _test_normality(df[col])

        results[col] = col_stats

    return results


def _comparative_analysis(
    df,
    target_columns: List[str],
    group_by_columns: Optional[List[str]],
    aggregation_method: str,
    statistical_tests: bool,
) -> Dict[str, Any]:
    """Perform comparative analysis across groups"""

    if not group_by_columns:
        # If no grouping specified, try to find categorical columns
        pl = get_polars()
        group_by_columns = [
            col
            for col in df.columns
            if df[col].dtype == pl.Utf8 and df[col].n_unique() < 20
        ]

    if not group_by_columns:
        return {"error": "No grouping columns available for comparative analysis"}

    results = {}

    for group_col in group_by_columns:  # Process all grouping columns
        for target_col in target_columns:  # Process all target columns
            # Build aggregation expression
            agg_expr = _get_aggregation_expression(target_col, aggregation_method)

            # Group by analysis
            grouped = (
                df.group_by(group_col)
                .agg(
                    [
                        agg_expr.alias("value"),
                        pl.col(target_col).count().alias("count"),
                        pl.col(target_col).mean().alias("mean"),
                        pl.col(target_col).std().alias("std"),
                        pl.col(target_col).min().alias("min"),
                        pl.col(target_col).max().alias("max"),
                    ]
                )
                .sort("value", descending=True)
            )

            # Calculate relative performance
            total_value = grouped["value"].sum()
            group_data = []

            for row in grouped.to_dicts():
                row_data = row.copy()
                row_data["percentage_of_total"] = (
                    (row["value"] / total_value * 100) if total_value != 0 else 0
                )
                row_data["performance_vs_mean"] = (
                    (row["mean"] - grouped["mean"].mean())
                    / grouped["mean"].mean()
                    * 100
                    if grouped["mean"].mean() and grouped["mean"].mean() != 0
                    else 0
                )
                group_data.append(row_data)

            # Statistical tests between groups if requested
            comparison_stats = {
                "groups": group_data,
                "total_groups": len(group_data),
                "performance_gap_pct": (
                    (group_data[0]["mean"] - group_data[-1]["mean"])
                    / group_data[-1]["mean"]
                    * 100
                    if len(group_data) > 1 and group_data[-1]["mean"] != 0
                    else 0
                ),
            }

            if statistical_tests and len(group_data) > 1:
                comparison_stats["statistical_tests"] = _perform_group_comparison_tests(
                    df, group_col, target_col
                )

            results[f"{group_col}_by_{target_col}"] = comparison_stats

    return results


def _temporal_analysis(
    df,
    target_columns: List[str],
    time_column: Optional[str],
    window_size: int,
    trend_periods: int,
    aggregation_method: str,
) -> Dict[str, Any]:
    """Perform temporal analysis"""

    # Auto-detect time column if not specified
    pl = get_polars()
    if not time_column:
        date_cols = [
            col for col in df.columns if df[col].dtype in [pl.Date, pl.Datetime]
        ]
        if date_cols:
            time_column = date_cols[0]
        else:
            # Use row index as proxy for time
            df = df.with_row_index("time_index")
            time_column = "time_index"

    results = {}

    # Sort by time column
    df_sorted = df.sort(time_column)

    for col in target_columns:
        if col not in df.columns:
            continue

        # Calculate moving averages and trends
        temporal_df = df_sorted.with_columns(
            [
                pl.col(col).rolling_mean(window_size=window_size).alias("moving_avg"),
                pl.col(col).rolling_std(window_size=window_size).alias("moving_std"),
                pl.col(col).pct_change().alias("pct_change"),
                pl.col(col).diff().alias("abs_change"),
            ]
        )

        # Trend analysis
        recent_data = temporal_df.tail(trend_periods)

        # Calculate trend metrics
        values = recent_data[col].to_list()
        if len(values) > 1:
            # Simple linear trend
            x = list(range(len(values)))
            y = [v for v in values if v is not None]
            if len(y) > 1:
                slope = _calculate_trend_slope(x[: len(y)], y)
            else:
                slope = 0
        else:
            slope = 0

        # Seasonality detection (basic)
        seasonality = _detect_seasonality(temporal_df[col].to_list())

        # Volatility metrics
        pct_changes = temporal_df["pct_change"].drop_nulls()
        volatility = float(pct_changes.std()) if len(pct_changes) > 0 else 0

        # Percent change metrics (overall, last period, average) and MoM/YoY if monthly data exists
        series_all = df_sorted[col].to_list()
        non_null_series = [v for v in series_all if v is not None]
        overall_change_pct = None
        if len(non_null_series) >= 2 and non_null_series[0] not in (0, None):
            try:
                overall_change_pct = (
                    (non_null_series[-1] - non_null_series[0])
                    / non_null_series[0]
                    * 100
                )
            except Exception:
                overall_change_pct = None
        last_period_change_pct = None
        avg_period_change_pct = None
        try:
            if len(pct_changes) > 0:
                last_val = pct_changes.tail(1).item()
                last_period_change_pct = (
                    float(last_val) * 100 if last_val is not None else None
                )
                avg_period_change_pct = (
                    float(pct_changes.mean()) * 100 if pct_changes.len() > 0 else None
                )
        except Exception:
            pass

        # Month-over-month and YoY change if year/month exist
        mom_change_pct = None
        avg_mom_change_pct = None
        yoy_change_pct = None
        same_months_yoy: Dict[int, float] | None = None
        # Placeholders for enhanced seasonality reporting
        seasonality_details = None
        seasonality_strength = None
        seasonality_examples = None
        # Placeholder for per-product analysis
        per_product_analysis = None
        # Case A: anio + mes present (multi-year aware)
        if "anio" in df.columns and "mes" in df.columns:
            try:
                # CRITICAL FIX: Aggregate by time period first to get total sales trends, not individual product trends
                agg_expr = _get_aggregation_expression(col, aggregation_method)
                monthly = df.select(
                    [
                        pl.col("anio").cast(pl.Int64),
                        pl.col("mes").cast(pl.Int64),
                        pl.col(col),
                    ]
                ).drop_nulls()
                # Aggregate by year-month to get totals across all products/entities
                monthly = (
                    monthly.group_by(["anio", "mes"])
                    .agg([agg_expr.alias(col)])
                    .sort(["anio", "mes"])
                )
                rows = monthly.to_dicts()
                # Build ordered list of (y,m,val) with aggregated values
                ordered = [
                    (int(r["anio"]), int(r["mes"]), r[col])
                    for r in rows
                    if r.get(col) is not None
                ]
                # Quick lookup and structures
                val_map = {(y, m): v for (y, m, v) in ordered}
                years = sorted({y for (y, m, v) in ordered})
                months_by_year = {
                    y: sorted({m for (yy, m, v) in ordered if yy == y}) for y in years
                }

                # Compute latest MoM (consecutive months across boundary allowed)
                if len(ordered) >= 2:
                    y, m, v = ordered[-1]
                    py, pm, pv = ordered[-2]
                    is_consecutive = (py == y and pm == m - 1) or (
                        py == y - 1 and pm == 12 and m == 1
                    )
                    if is_consecutive and pv not in (0, None):
                        mom_change_pct = (v - pv) / pv * 100
                # Average MoM across consecutive pairs
                deltas = []
                for i in range(1, len(ordered)):
                    y2, m2, v2 = ordered[i]
                    y1, m1, v1 = ordered[i - 1]
                    is_consec = (y1 == y2 and m1 == m2 - 1) or (
                        y1 == y2 - 1 and m1 == 12 and m2 == 1
                    )
                    if is_consec and v1 not in (0, None) and v2 is not None:
                        try:
                            deltas.append((v2 - v1) / v1 * 100)
                        except Exception:
                            continue
                if deltas:
                    avg_mom_change_pct = float(sum(deltas) / len(deltas))
                # YoY last month if same month last year exists
                if ordered:
                    y, m, v = ordered[-1]
                    # Find previous year same month
                    for yy, mm, vv in reversed(ordered[:-1]):
                        if yy == y - 1 and mm == m and vv not in (0, None):
                            yoy_change_pct = (v - vv) / vv * 100
                            break
                # Same-month across years (latest year vs previous year)
                if ordered:
                    latest_year = years[-1]
                    prev_year = years[-2] if len(years) >= 2 else None
                    if prev_year is not None:
                        same_months_yoy = {}
                        months_in_latest = months_by_year.get(latest_year, [])
                        for m in months_in_latest:
                            v_cur = val_map.get((latest_year, m))
                            v_prev = val_map.get((prev_year, m))
                            if v_cur is not None and v_prev not in (None, 0):
                                try:
                                    same_months_yoy[m] = (v_cur - v_prev) / v_prev * 100
                                except Exception:
                                    continue
                # Full MoM series per year (m2 vs m1, m3 vs m2, ...)
                mom_series_by_year = {}
                for y in years:
                    months = months_by_year.get(y, [])
                    if len(months) >= 2:
                        series = {}
                        for i in range(1, len(months)):
                            m_curr = months[i]
                            m_prev = months[i - 1]
                            v_prev = val_map.get((y, m_prev))
                            v_curr = val_map.get((y, m_curr))
                            if v_prev not in (None, 0) and v_curr is not None:
                                try:
                                    series[m_curr] = (v_curr - v_prev) / v_prev * 100
                                except Exception:
                                    continue
                        if series:
                            mom_series_by_year[y] = series
                # Full YoY series per year (year vs previous year by month)
                yoy_series_by_year = {}
                for idx in range(1, len(years)):
                    y = years[idx]
                    prev = years[idx - 1]
                    series = {}
                    for m in months_by_year.get(y, []):
                        v_cur = val_map.get((y, m))
                        v_prev = val_map.get((prev, m))
                        if v_cur is not None and v_prev not in (None, 0):
                            try:
                                series[m] = (v_cur - v_prev) / v_prev * 100
                            except Exception:
                                continue
                    if series:
                        yoy_series_by_year[y] = series
                # Year totals and YoY at year-level
                try:
                    agg_expr = _get_aggregation_expression(col, aggregation_method)
                    year_totals_df = (
                        monthly.group_by("anio")
                        .agg([agg_expr.alias("value")])
                        .sort("anio")
                    )
                    year_totals = {
                        int(r["anio"]): r["value"] for r in year_totals_df.to_dicts()
                    }
                    yoy_year_series = {}
                    years_sorted = sorted(year_totals.keys())
                    for i in range(1, len(years_sorted)):
                        y = years_sorted[i]
                        p = years_sorted[i - 1]
                        v_cur = year_totals.get(y)
                        v_prev = year_totals.get(p)
                        if v_cur is not None and v_prev not in (None, 0):
                            try:
                                yoy_year_series[y] = (v_cur - v_prev) / v_prev * 100
                            except Exception:
                                continue
                    yoy_year_change_pct = None
                    if len(years_sorted) >= 2:
                        ly = years_sorted[-1]
                        py = years_sorted[-2]
                        v_ly = year_totals.get(ly)
                        v_py = year_totals.get(py)
                        if v_ly is not None and v_py not in (None, 0):
                            yoy_year_change_pct = (v_ly - v_py) / v_py * 100
                except Exception:
                    year_totals = None
                    yoy_year_series = None
                    yoy_year_change_pct = None

                # Enhanced seasonality details across years by month
                try:
                    month_groups = {}
                    for (yy, mm), vv in val_map.items():
                        if vv is None:
                            continue
                        m_int = int(mm)
                        month_groups.setdefault(m_int, []).append(vv)
                    month_means = {
                        m: float(get_numpy().mean(vals))
                        for m, vals in month_groups.items()
                        if vals
                    }
                    if month_means:
                        overall = float(get_numpy().mean(list(month_means.values())))
                        if overall > 0:
                            month_index = {
                                m: month_means[m] / overall for m in month_means
                            }
                            high_months = sorted(
                                [m for m, idx in month_index.items() if idx >= 1.10]
                            )
                            low_months = sorted(
                                [m for m, idx in month_index.items() if idx <= 0.90]
                            )

                            def _build_ranges(ms: List[int]) -> List[str]:
                                if not ms:
                                    return []
                                ms = sorted(ms)
                                ranges = []
                                start = ms[0]
                                prev = ms[0]
                                for m in ms[1:]:
                                    if m == prev + 1:
                                        prev = m
                                        continue
                                    ranges.append((start, prev))
                                    start = m
                                    prev = m
                                ranges.append((start, prev))
                                month_names = {
                                    1: "Ene",
                                    2: "Feb",
                                    3: "Mar",
                                    4: "Abr",
                                    5: "May",
                                    6: "Jun",
                                    7: "Jul",
                                    8: "Ago",
                                    9: "Sep",
                                    10: "Oct",
                                    11: "Nov",
                                    12: "Dic",
                                }
                                out = []
                                for a, b in ranges:
                                    if a == b:
                                        out.append(month_names.get(a, str(a)))
                                    else:
                                        out.append(
                                            f"{month_names.get(a, str(a))}–{month_names.get(b, str(b))}"
                                        )
                                return out

                            high_ranges = _build_ranges(high_months)
                            low_ranges = _build_ranges(low_months)
                            amplitude = (
                                (max(month_means.values()) - min(month_means.values()))
                                / overall
                                if overall
                                else 0.0
                            )
                            seasonality_strength = (
                                "fuerte"
                                if amplitude >= 0.30
                                else "moderada"
                                if amplitude >= 0.15
                                else "débil"
                            )
                            seasonality_details = {
                                "month_means": month_means,
                                "overall_mean_by_month": overall,
                                "high_months": high_months,
                                "low_months": low_months,
                                "high_ranges": high_ranges,
                                "low_ranges": low_ranges,
                                "amplitude_ratio": amplitude,
                            }
                            parts = []
                            if high_ranges:
                                parts.append(f"Altos: {', '.join(high_ranges)}")
                            if low_ranges:
                                parts.append(f"Bajos: {', '.join(low_ranges)}")
                            seasonality_examples = " | ".join(parts) if parts else None
                            if high_months or low_months:
                                seasonality = True
                except Exception:
                    pass

                # Per-product analysis for multi-year monthly data
                try:
                    per_product_analysis = _analyze_per_product_trends(
                        df, col, aggregation_method, "anio", "mes"
                    )
                except Exception:
                    per_product_analysis = None
            except Exception:
                pass
        # Case B: only mes present (single-year monthly)
        elif "mes" in df.columns:
            try:
                # CRITICAL FIX: Aggregate by month first to get total sales trends, not individual product trends
                agg_expr = _get_aggregation_expression(col, aggregation_method)
                monthly_agg = df.select(
                    [pl.col("mes").cast(pl.Int64), pl.col(col)]
                ).drop_nulls()
                # Aggregate by month to get totals across all products/entities
                monthly_agg = (
                    monthly_agg.group_by("mes")
                    .agg([agg_expr.alias("value")])
                    .sort("mes")
                )

                dicts = monthly_agg.to_dicts()
                vals = [r["value"] for r in dicts if r.get("value") is not None]
                months = [r["mes"] for r in dicts if r.get("value") is not None]

                # Calculate latest MoM change with proper aggregated values
                if len(vals) >= 2 and vals[-2] not in (None, 0):
                    # Use a minimum threshold to avoid extreme percentages from very small values
                    min_threshold = max(
                        abs(vals[-2]) * 0.001, 1.0
                    )  # 0.1% of previous value or 1, whichever is larger
                    if abs(vals[-2]) >= min_threshold:
                        mom_change_pct = (vals[-1] - vals[-2]) / vals[-2] * 100
                        # Cap extreme changes to reasonable values
                        mom_change_pct = max(-99.9, min(999.9, mom_change_pct))

                # Calculate average MoM using consecutive month pairs
                deltas = []
                for i in range(1, len(vals)):
                    prev_v = vals[i - 1]
                    cur_v = vals[i]
                    if prev_v not in (None, 0) and cur_v is not None:
                        min_threshold = max(abs(prev_v) * 0.001, 1.0)
                        if abs(prev_v) >= min_threshold:
                            try:
                                delta = (cur_v - prev_v) / prev_v * 100
                                # Cap individual deltas to avoid extreme averages
                                delta = max(-99.9, min(999.9, delta))
                                deltas.append(delta)
                            except Exception:
                                continue
                if deltas:
                    avg_mom_change_pct = float(sum(deltas) / len(deltas))

                # Build full MoM series for single-year data with validation
                mom_series_flat = {}
                for i in range(1, len(vals)):
                    prev_v = vals[i - 1]
                    cur_v = vals[i]
                    m_cur = int(months[i])
                    if prev_v not in (None, 0) and cur_v is not None:
                        min_threshold = max(abs(prev_v) * 0.001, 1.0)
                        if abs(prev_v) >= min_threshold:
                            try:
                                mom_pct = (cur_v - prev_v) / prev_v * 100
                                # Cap extreme changes
                                mom_pct = max(-99.9, min(999.9, mom_pct))
                                mom_series_flat[m_cur] = mom_pct
                            except Exception:
                                continue

                # Enhanced seasonality details within single-year monthly data
                try:
                    if months and vals:
                        month_means = {
                            int(m): float(v)
                            for m, v in zip(months, vals)
                            if v is not None
                        }
                        overall = (
                            float(get_numpy().mean(list(month_means.values())))
                            if month_means
                            else 0.0
                        )
                        if overall > 0:
                            month_index = {
                                m: month_means[m] / overall for m in month_means
                            }
                            high_months = sorted(
                                [m for m, idx in month_index.items() if idx >= 1.10]
                            )
                            low_months = sorted(
                                [m for m, idx in month_index.items() if idx <= 0.90]
                            )

                            def _build_ranges(ms: List[int]) -> List[str]:
                                if not ms:
                                    return []
                                ms = sorted(ms)
                                ranges = []
                                start = ms[0]
                                prev = ms[0]
                                for m in ms[1:]:
                                    if m == prev + 1:
                                        prev = m
                                        continue
                                    ranges.append((start, prev))
                                    start = m
                                    prev = m
                                ranges.append((start, prev))
                                month_names = {
                                    1: "Ene",
                                    2: "Feb",
                                    3: "Mar",
                                    4: "Abr",
                                    5: "May",
                                    6: "Jun",
                                    7: "Jul",
                                    8: "Ago",
                                    9: "Sep",
                                    10: "Oct",
                                    11: "Nov",
                                    12: "Dic",
                                }
                                out = []
                                for a, b in ranges:
                                    if a == b:
                                        out.append(month_names.get(a, str(a)))
                                    else:
                                        out.append(
                                            f"{month_names.get(a, str(a))}–{month_names.get(b, str(b))}"
                                        )
                                return out

                            high_ranges = _build_ranges(high_months)
                            low_ranges = _build_ranges(low_months)
                            amplitude = (
                                (max(month_means.values()) - min(month_means.values()))
                                / overall
                                if overall
                                else 0.0
                            )
                            seasonality_strength = (
                                "fuerte"
                                if amplitude >= 0.30
                                else "moderada"
                                if amplitude >= 0.15
                                else "débil"
                            )
                            seasonality_details = {
                                "month_means": month_means,
                                "overall_mean_by_month": overall,
                                "high_months": high_months,
                                "low_months": low_months,
                                "high_ranges": high_ranges,
                                "low_ranges": low_ranges,
                                "amplitude_ratio": amplitude,
                            }
                            parts = []
                            if high_ranges:
                                parts.append(f"Altos: {', '.join(high_ranges)}")
                            if low_ranges:
                                parts.append(f"Bajos: {', '.join(low_ranges)}")
                            seasonality_examples = " | ".join(parts) if parts else None
                            if high_months or low_months:
                                seasonality = True
                except Exception:
                    pass
            except Exception:
                pass
        # Case C: yearly data only
        elif "anio" in df.columns:
            try:
                yearly = df.select(
                    [pl.col("anio").cast(pl.Int64), pl.col(col)]
                ).drop_nulls()
                # Aggregate by year using configured method in case input has duplicates
                agg_expr = _get_aggregation_expression(col, aggregation_method)
                year_totals_df = (
                    yearly.group_by("anio").agg([agg_expr.alias("value")]).sort("anio")
                )
                year_totals = {
                    int(r["anio"]): r["value"] for r in year_totals_df.to_dicts()
                }
                # Build YoY series per year
                yoy_year_series = {}
                years_sorted = sorted(year_totals.keys())
                for i in range(1, len(years_sorted)):
                    y = years_sorted[i]
                    p = years_sorted[i - 1]
                    v_cur = year_totals.get(y)
                    v_prev = year_totals.get(p)
                    if v_cur is not None and v_prev not in (None, 0):
                        try:
                            yoy_year_series[y] = (v_cur - v_prev) / v_prev * 100
                        except Exception:
                            continue
                yoy_year_change_pct = None
                if len(years_sorted) >= 2:
                    ly = years_sorted[-1]
                    py = years_sorted[-2]
                    v_ly = year_totals.get(ly)
                    v_py = year_totals.get(py)
                    if v_ly is not None and v_py not in (None, 0):
                        yoy_year_change_pct = (v_ly - v_py) / v_py * 100
            except Exception:
                year_totals = None
                yoy_year_series = None
                yoy_year_change_pct = None

        trend_info = {
            "trend_slope": slope,
            "trend_direction": "creciente"
            if slope > 0.01
            else "decreciente"
            if slope < -0.01
            else "estable",
            "volatility": volatility,
            "volatility_level": "alta"
            if volatility > 0.2
            else "media"
            if volatility > 0.1
            else "baja",
            "seasonality_detected": seasonality,
            # Keep legacy recent_change_pct semantics (fractional mean); new fields below are in percent units
            "recent_change_pct": float(recent_data["pct_change"].mean())
            if len(recent_data) > 0
            else 0,
            "last_period_change_pct": last_period_change_pct,
            "avg_period_change_pct": avg_period_change_pct,
            "overall_change_pct": overall_change_pct,
            "mom_change_pct": mom_change_pct,
            "avg_mom_change_pct": avg_mom_change_pct,
            "yoy_change_pct": yoy_change_pct,
            "same_months_yoy": same_months_yoy,
            "mom_series": mom_series_by_year
            if "mom_series_by_year" in locals() and mom_series_by_year
            else (mom_series_flat if "mom_series_flat" in locals() else None),
            "yoy_series": yoy_series_by_year
            if "yoy_series_by_year" in locals() and yoy_series_by_year
            else None,
            "year_totals": year_totals if "year_totals" in locals() else None,
            "yoy_year_series": yoy_year_series
            if "yoy_year_series" in locals()
            else None,
            "yoy_year_change_pct": yoy_year_change_pct
            if "yoy_year_change_pct" in locals()
            else None,
            "periods_analyzed": len(values),
        }

        # Attach enhanced seasonality details when available
        if seasonality_details is not None:
            trend_info["seasonality_details"] = seasonality_details
        if seasonality_strength is not None:
            trend_info["seasonality_strength"] = seasonality_strength
        if seasonality_examples is not None:
            trend_info["seasonality_examples"] = seasonality_examples

        # Attach per-product analysis when available
        if per_product_analysis is not None:
            trend_info["per_product_analysis"] = per_product_analysis

        # Add moving average analysis
        if len(temporal_df) > window_size:
            current_value = temporal_df[col].tail(1).item()
            current_ma = temporal_df["moving_avg"].tail(1).item()

            if current_value and current_ma:
                trend_info["vs_moving_avg"] = (
                    (current_value - current_ma) / current_ma * 100
                )

        results[col] = trend_info

    return results


def _correlation_analysis(
    df,
    target_columns: List[str],
    correlation_threshold: float,
    method: str = "pearson",
    **kwargs,
) -> Dict[str, Any]:
    """Perform correlation analysis"""

    if len(target_columns) < 2:
        return {"error": "Need at least 2 numeric columns for correlation analysis"}

    correlations = {}
    significant_correlations = []

    # Calculate pairwise correlations
    for i, col1 in enumerate(target_columns):
        for col2 in target_columns[i + 1 :]:
            try:
                # Calculate Pearson correlation using Polars expression (robust to nulls and constant series)
                pairs = df.select([pl.col(col1), pl.col(col2)]).drop_nulls()
                if pairs.height < 2:
                    continue
                corr_value = pairs.select(
                    pl.corr(pl.col(col1), pl.col(col2)).alias("corr")
                ).to_series()[0]

                if corr_value is not None and not (
                    np.isnan(corr_value) or np.isinf(corr_value)
                ):
                    abs_corr = abs(float(corr_value))

                    # Only report correlations above threshold
                    if abs_corr >= correlation_threshold:
                        correlation_info = {
                            "correlation": float(corr_value),
                            "strength": _interpret_correlation_strength(abs_corr),
                            "direction": "positiva" if corr_value > 0 else "negativa",
                            "significance": "alta"
                            if abs_corr > 0.7
                            else "media"
                            if abs_corr > 0.5
                            else "baja",
                        }

                        correlations[f"{col1}_vs_{col2}"] = correlation_info

                        if abs_corr > 0.5:  # Significant correlations
                            significant_correlations.append(
                                {
                                    "variables": f"{col1} - {col2}",
                                    "correlation": float(corr_value),
                                    "interpretation": f"Correlación {correlation_info['strength']} {correlation_info['direction']}",
                                }
                            )

            except Exception as e:
                correlations[f"{col1}_vs_{col2}"] = {"error": str(e)}

    return {
        "correlations": correlations,
        "significant_correlations": significant_correlations,
        "correlation_matrix_available": len(correlations) > 0,
        "threshold_used": correlation_threshold,
    }


def _distribution_analysis(
    df, target_columns: List[str], percentiles: List[float], bins: int = 10, **kwargs
) -> Dict[str, Any]:
    """Analyze data distributions with automatic grouping by entity columns when appropriate"""

    results = {}

    # Detectar columnas de entidad automáticamente para agrupación
    pl = get_polars()
    entity_columns = []
    for col in df.columns:
        if df[col].dtype == pl.Utf8:
            unique_count = df[col].n_unique()
            # Identificar columnas que parecen ser entidades (producto, cliente, etc.)
            col_lower = col.lower()
            is_entity_name = any(
                pattern in col_lower
                for pattern in [
                    "producto",
                    "product",
                    "cliente",
                    "customer",
                    "sku",
                    "codigo",
                    "marca",
                    "brand",
                    "categoria",
                    "category",
                    "tipo",
                    "type",
                    "grupo",
                    "group",
                ]
            )
            # Cardinalidad razonable para agrupación (entre 2 y 50 valores únicos)
            reasonable_cardinality = 2 <= unique_count <= 50

            if is_entity_name and reasonable_cardinality:
                entity_columns.append(col)

    # Si encontramos columnas de entidad, hacer análisis agrupado para métricas de distribución
    grouped_analysis = {}
    if entity_columns:
        primary_entity = entity_columns[0]  # Usar la primera entidad encontrada

        for col in target_columns:
            if col not in df.columns:
                continue

            # Análisis de distribución agrupado por entidad
            try:
                pl = get_polars()
                grouped_stats = (
                    df.group_by(primary_entity)
                    .agg(
                        [
                            pl.col(col).count().alias("count"),
                            pl.col(col).mean().alias("mean"),
                            pl.col(col).std().alias("std"),
                            pl.col(col).min().alias("min"),
                            pl.col(col).max().alias("max"),
                            pl.col(col).quantile(0.25).alias("q1"),
                            pl.col(col).median().alias("median"),
                            pl.col(col).quantile(0.75).alias("q3"),
                        ]
                    )
                    .sort("mean", descending=True)
                )

                # Calcular skewness y kurtosis por grupo
                group_distributions = []
                for row in grouped_stats.to_dicts():
                    entity_value = row[primary_entity]
                    entity_data = df.filter(pl.col(primary_entity) == entity_value)[
                        col
                    ].drop_nulls()

                    if len(entity_data) > 2:
                        values = entity_data.to_list()
                        skewness = (
                            float(get_scipy_stats().skew(values))
                            if len(values) > 2
                            else 0.0
                        )
                        kurtosis = (
                            float(get_scipy_stats().kurtosis(values))
                            if len(values) > 2
                            else 0.0
                        )
                    else:
                        skewness = 0.0
                        kurtosis = 0.0

                    row["skewness"] = skewness
                    row["kurtosis"] = kurtosis
                    row["distribution_shape"] = _classify_distribution_shape(
                        skewness, kurtosis
                    )
                    group_distributions.append(row)

                grouped_analysis[col] = {
                    "grouped_by": primary_entity,
                    "group_distributions": group_distributions,
                    "total_groups": len(group_distributions),
                    "auto_grouped": True,
                    "reason": f'Detectada columna de entidad "{primary_entity}" - agrupación automática aplicada para análisis de distribución apropiado',
                }

            except Exception as e:
                # Si falla el análisis agrupado, continuar con análisis normal
                pass

    for col in target_columns:
        if col not in df.columns:
            continue

        # Basic distribution stats
        col_data = df[col].drop_nulls()

        if len(col_data) == 0:
            results[col] = {"error": "No valid data for distribution analysis"}
            continue

        # Calculate distribution metrics using scipy
        col_values = col_data.to_list()
        if col_values and len(col_values) > 1:
            skewness_val = float(get_scipy_stats().skew(col_values))
            kurtosis_val = float(get_scipy_stats().kurtosis(col_values))
        else:
            skewness_val = 0.0
            kurtosis_val = 0.0

        distribution_stats = {
            "skewness": skewness_val,
            "kurtosis": kurtosis_val,
            "distribution_shape": _classify_distribution_shape(
                skewness_val, kurtosis_val
            ),
        }

        # Percentile analysis
        percentile_data = {}
        for p in percentiles:
            percentile_data[f"p{int(p * 100)}"] = float(col_data.quantile(p))

        distribution_stats["percentiles"] = percentile_data

        # Histogram data (for visualization)
        min_val, max_val = float(col_data.min()), float(col_data.max())
        if min_val != max_val:
            hist_data = _create_histogram_data(
                col_data.to_list(), bins, min_val, max_val
            )
            distribution_stats["histogram"] = hist_data

        results[col] = distribution_stats

    return results


def _ranking_analysis(
    df,
    target_columns: List[str],
    group_by_columns: Optional[List[str]],
    aggregation_method: str,
    top_n: int = 10,
    **kwargs,
) -> Dict[str, Any]:
    """Perform ranking analysis"""

    results = {}

    for col in target_columns:
        if col not in df.columns:
            continue

        # Overall rankings
        top_performers = df.top_k(min(top_n, df.height), by=col)
        bottom_performers = df.bottom_k(min(top_n, df.height), by=col)

        ranking_info = {
            "top_performers": top_performers.to_dicts(),
            "bottom_performers": bottom_performers.to_dicts(),
            "performance_gap": float(df[col].max() - df[col].min())
            if df[col].max() and df[col].min()
            else 0,
        }

        # Grouped rankings if specified
        if group_by_columns:
            for group_col in group_by_columns:  # Process all grouping columns
                if group_col in df.columns:
                    group_rankings = (
                        df.group_by(group_col)
                        .agg(
                            [
                                _get_aggregation_expression(
                                    col, aggregation_method
                                ).alias("value")
                            ]
                        )
                        .sort("value", descending=True)
                    )

                    ranking_info[f"by_{group_col}"] = group_rankings.to_dicts()

        results[col] = ranking_info

    return results


def _outlier_analysis(
    df, target_columns: List[str], method: str, threshold: float, **kwargs
) -> Dict[str, Any]:
    """Detect and analyze outliers"""

    results = {}

    for col in target_columns:
        if col not in df.columns:
            continue

        outliers_info = {"method": method, "threshold": threshold}

        if method == "iqr":
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - threshold * iqr
            upper_bound = q3 + threshold * iqr

            pl = get_polars()
            outliers = df.filter(
                (pl.col(col) < lower_bound) | (pl.col(col) > upper_bound)
            )

            outliers_info.update(
                {
                    "bounds": {
                        "lower": float(lower_bound),
                        "upper": float(upper_bound),
                    },
                    "outliers_count": outliers.height,
                    "outliers_percentage": (outliers.height / df.height) * 100,
                    "outlier_values": outliers[col].to_list(),
                }
            )

        elif method == "zscore":
            mean_val = df[col].mean()
            std_val = df[col].std()

            if std_val and std_val != 0:
                z_scores = (df[col] - mean_val) / std_val
                pl = get_polars()
                outliers = df.filter(pl.abs(z_scores) > threshold)

                outliers_info.update(
                    {
                        "z_threshold": threshold,
                        "outliers_count": outliers.height,
                        "outliers_percentage": (outliers.height / df.height) * 100,
                        "outlier_values": outliers[col].to_list(),
                    }
                )

        results[col] = outliers_info

    return results


def _regression_analysis(
    df, target_columns: List[str], target_variable: Optional[str] = None, **kwargs
) -> Dict[str, Any]:
    """Perform basic regression analysis"""

    if not target_variable:
        target_variable = target_columns[0] if target_columns else None

    if not target_variable or len(target_columns) < 2:
        return {"error": "Need at least 2 variables for regression analysis"}

    predictors = [col for col in target_columns if col != target_variable]

    results = {"target_variable": target_variable, "predictors": predictors}

    # Simple linear regression for each predictor
    for predictor in predictors:  # Process all predictors
        try:
            # Calculate Pearson correlation as a proxy for relationship strength (robust)
            pairs = df.select([pl.col(target_variable), pl.col(predictor)]).drop_nulls()
            if pairs.height < 2:
                continue
            correlation = pairs.select(
                pl.corr(pl.col(target_variable), pl.col(predictor)).alias("corr")
            ).to_series()[0]

            if correlation is not None and not (
                np.isnan(correlation) or np.isinf(correlation)
            ):
                r_squared = float(correlation) ** 2

                results[f"{predictor}_regression"] = {
                    "correlation": float(correlation),
                    "r_squared": float(r_squared),
                    "relationship_strength": _interpret_correlation_strength(
                        abs(float(correlation))
                    ),
                }
        except Exception as e:
            results[f"{predictor}_regression"] = {"error": str(e)}

    return results


# Helper functions
def _parse_markdown_table(data: str):
    """Parse markdown table format with robust handling for pandas-style tables.
    Correctly detects and skips a leftmost index column even when the header cell is empty.
    """
    lines = [line.strip() for line in data.split("\n") if "|" in line and line.strip()]
    if len(lines) < 2:
        return None

    # Patterns
    alignment_re = re.compile(r"^\s*\|[\s\|\-:]+\|\s*$")

    # Locate header and data start
    header_idx = None
    data_start_idx = 0
    for i, line in enumerate(lines):
        if alignment_re.match(line):
            if header_idx is None and i > 0:
                header_idx = i - 1
            data_start_idx = i + 1
            break
    if header_idx is None:
        header_idx = 0
        data_start_idx = 1

    # Raw header cells (preserve empties for index detection)
    raw_header_cells = [c.strip() for c in lines[header_idx].strip("|").split("|")]
    if not raw_header_cells:
        return None

    # Detect index-like first column
    first_cell = raw_header_cells[0] if raw_header_cells else ""
    drop_first = False
    if (
        first_cell == ""
        or first_cell.isdigit()
        or re.fullmatch(r"(?:index|idx|#|unnamed[:\s]*0?)", first_cell, re.IGNORECASE)
    ):
        drop_first = True

    # Build final headers from raw cells, dropping the first if it's index-like
    header_cells = raw_header_cells[1:] if drop_first else raw_header_cells[:]
    # Replace any empty header names with generic ones
    if any(h == "" for h in header_cells):
        header_cells = [
            h if h != "" else f"col_{i}" for i, h in enumerate(header_cells)
        ]

    # Extract data rows
    data_rows = []
    for line in lines[data_start_idx:]:
        # Skip alignment lines inside the body
        if alignment_re.match(line):
            continue
        if not (line.startswith("|") and line.endswith("|")):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if drop_first and len(cells) > 0:
            cells = cells[1:]
        # Align to header length
        if len(cells) < len(header_cells):
            cells += [""] * (len(header_cells) - len(cells))
        elif len(cells) > len(header_cells):
            cells = cells[: len(header_cells)]
        if any(c.strip() for c in cells):
            data_rows.append(cells)

    if not data_rows:
        return None

    # Create DataFrame with robust fallbacks
    pl = get_polars()
    try:
        df = pl.DataFrame(data_rows, schema=header_cells, orient="row")
        return _infer_column_types(df)
    except Exception:
        try:
            generic_headers = [f"col_{i}" for i in range(len(data_rows[0]))]
            df = pl.DataFrame(data_rows, schema=generic_headers, orient="row")
            return _infer_column_types(df)
        except Exception:
            try:
                pd = get_pandas()
                from io import StringIO

                table_lines = []
                if drop_first:
                    table_lines.append("|idx|" + "|".join(header_cells) + "|")
                    table_lines.append(
                        "|-|" + "|".join(["-"] * len(header_cells)) + "|"
                    )
                    for i, row in enumerate(data_rows):
                        table_lines.append(f"|{i}|" + "|".join(row) + "|")
                else:
                    table_lines.append("|" + "|".join(header_cells) + "|")
                    table_lines.append("|" + "|".join(["-"] * len(header_cells)) + "|")
                    for row in data_rows:
                        table_lines.append("|" + "|".join(row) + "|")

                table_str = "\n".join(table_lines)
                pd_df = pd.read_table(
                    StringIO(table_str), sep="|", skipinitialspace=True
                )
                pd_df = pd_df.dropna(axis=1, how="all")
                df = pl.from_pandas(pd_df)
                return _infer_column_types(df)
            except Exception:
                return None


def _parse_csv_format(data: str):
    """Parse CSV format"""
    from io import StringIO

    try:
        pl = get_polars()
        df = pl.read_csv(StringIO(data))
        return _infer_column_types(df)
    except Exception:
        return None


def _parse_json_format(data: str):
    """Parse JSON format"""
    try:
        json_objects = re.findall(r"\{[^{}]*\}", data)
        if not json_objects:
            return None

        parsed_data = []
        for obj in json_objects:
            try:
                parsed_data.append(json.loads(obj))
            except json.JSONDecodeError:
                continue

        if parsed_data:
            pl = get_polars()
            df = pl.DataFrame(parsed_data)
            return _infer_column_types(df)
    except Exception:
        pass

    return None


def _infer_column_types(df):
    """Infer and cast appropriate data types with robust handling for various numeric formats"""
    pl = get_polars()
    cast_expressions = []

    for col in df.columns:
        col_series = df[col]

        # Skip already numeric columns
        if col_series.dtype in [pl.Int64, pl.Float64, pl.Int32, pl.Float32]:
            cast_expressions.append(pl.col(col))
            continue

        # Skip columns with all nulls
        if col_series.null_count() == len(col_series):
            cast_expressions.append(pl.col(col))
            continue

        try:
            # Get non-null values for type detection
            non_null_series = col_series.drop_nulls()

            if len(non_null_series) == 0:
                cast_expressions.append(pl.col(col))
                continue

            # Convert to string series for pattern matching
            str_series = non_null_series.cast(pl.Utf8)

            # Pattern for integers (including negative)
            integer_pattern = r"^\s*-?\d+\s*$"

            # Pattern for floats (including scientific notation, decimals, negatives)
            float_pattern = r"^\s*-?\d*\.?\d+([eE][+-]?\d+)?\s*$"

            # Pattern for dates
            date_pattern = r"\d{4}-\d{1,2}-\d{1,2}"

            # Check if all non-null values match integer pattern
            try:
                if str_series.str.contains(integer_pattern).all():
                    cast_expressions.append(
                        pl.col(col).str.strip_chars().cast(pl.Int64, strict=False)
                    )
                    continue
            except Exception:
                pass

            # Check if all non-null values match float pattern (including scientific notation)
            try:
                if str_series.str.contains(float_pattern).all():
                    cast_expressions.append(
                        pl.col(col).str.strip_chars().cast(pl.Float64, strict=False)
                    )
                    continue
            except Exception:
                pass

            # Check for date patterns
            try:
                if str_series.str.contains(date_pattern).any():
                    cast_expressions.append(
                        pl.col(col).str.strptime(pl.Date, "%Y-%m-%d", strict=False)
                    )
                    continue
            except Exception:
                pass

            # If no pattern matches, keep as string
            cast_expressions.append(pl.col(col))

        except Exception:
            # If any error occurs, keep the column as-is
            cast_expressions.append(pl.col(col))

    try:
        return df.with_columns(cast_expressions)
    except Exception:
        # If casting fails, return original DataFrame
        return df


def _get_aggregation_expression(column: str, method: str):
    """Get aggregation expression for given method"""
    pl = get_polars()
    method_map = {
        "sum": pl.col(column).sum(),
        "mean": pl.col(column).mean(),
        "median": pl.col(column).median(),
        "count": pl.col(column).count(),
        "min": pl.col(column).min(),
        "max": pl.col(column).max(),
        "std": pl.col(column).std(),
        "var": pl.col(column).var(),
    }
    return method_map.get(method, pl.col(column).sum())


def _calculate_confidence_intervals(
    series, confidence_level: float
) -> Dict[str, float]:
    """Calculate confidence intervals"""
    try:
        mean = series.mean()
        std = series.std()
        n = series.count()

        if mean and std and n > 1:
            # Simple confidence interval (assuming normal distribution)
            margin = (
                1.96 * (std / get_numpy().sqrt(n))
                if confidence_level == 0.95
                else 2.58 * (std / get_numpy().sqrt(n))
            )
            return {
                "lower": float(mean - margin),
                "upper": float(mean + margin),
                "confidence_level": confidence_level,
            }
    except Exception:
        pass

    return {"error": "Could not calculate confidence intervals"}


def _test_normality(series) -> Dict[str, Any]:
    """Basic normality test based on skewness and kurtosis"""
    try:
        skewness = series.skewness()
        kurtosis = series.kurtosis()

        # Simple heuristics for normality
        is_normal = (
            abs(skewness) < 2  # Not too skewed
            and abs(kurtosis) < 7  # Not too heavy/light tailed
        )

        return {
            "skewness": float(skewness) if skewness else 0,
            "kurtosis": float(kurtosis) if kurtosis else 0,
            "likely_normal": is_normal,
            "interpretation": "Likely normal" if is_normal else "Likely non-normal",
        }
    except Exception:
        return {"error": "Could not perform normality test"}


def _perform_group_comparison_tests(
    df, group_col: str, target_col: str
) -> Dict[str, Any]:
    """Perform basic statistical tests between groups"""
    try:
        pl = get_polars()
        groups = (
            df.group_by(group_col)
            .agg(
                [
                    pl.col(target_col).mean().alias("group_mean"),
                    pl.col(target_col).std().alias("group_std"),
                    pl.col(target_col).count().alias("group_count"),
                ]
            )
            .to_dicts()
        )

        if len(groups) >= 2:
            # Simple comparison between top 2 groups
            group1, group2 = groups[0], groups[1]

            # Effect size (Cohen's d approximation)
            pooled_std = (
                get_numpy().sqrt(
                    (
                        (group1["group_count"] - 1) * group1["group_std"] ** 2
                        + (group2["group_count"] - 1) * group2["group_std"] ** 2
                    )
                    / (group1["group_count"] + group2["group_count"] - 2)
                )
                if group1["group_std"] and group2["group_std"]
                else 1
            )

            effect_size = abs(group1["group_mean"] - group2["group_mean"]) / pooled_std

            return {
                "groups_compared": 2,
                "effect_size": effect_size,
                "effect_interpretation": (
                    "Large"
                    if effect_size > 0.8
                    else "Medium"
                    if effect_size > 0.5
                    else "Small"
                    if effect_size > 0.2
                    else "Negligible"
                ),
                "mean_difference": abs(group1["group_mean"] - group2["group_mean"]),
            }
    except Exception:
        pass

    return {"error": "Could not perform group comparison tests"}


def _calculate_trend_slope(x: List[int], y: List[float]) -> float:
    """Calculate simple linear trend slope"""
    try:
        if len(x) != len(y) or len(x) < 2:
            return 0

        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x_sq = sum(xi * xi for xi in x)

        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x_sq - sum_x * sum_x)
        return slope
    except Exception:
        return 0


def _detect_seasonality(values: List) -> bool:
    """Simple seasonality detection"""
    try:
        if len(values) < 12:  # Need at least 12 points for seasonality
            return False

        # Simple approach: check for repeating patterns
        # This is a very basic heuristic
        clean_values = [v for v in values if v is not None]
        if len(clean_values) < 6:
            return False

        # Check for cyclical behavior (very basic)
        mid_point = len(clean_values) // 2
        first_half_mean = get_numpy().mean(clean_values[:mid_point])
        second_half_mean = get_numpy().mean(clean_values[mid_point:])

        # If there's a significant difference, might indicate seasonality
        return abs(first_half_mean - second_half_mean) > 0.1 * first_half_mean

    except Exception:
        return False


def _interpret_correlation_strength(abs_correlation: float) -> str:
    """Interpret correlation strength"""
    if abs_correlation >= 0.9:
        return "muy fuerte"
    elif abs_correlation >= 0.7:
        return "fuerte"
    elif abs_correlation >= 0.5:
        return "moderada"
    elif abs_correlation >= 0.3:
        return "débil"
    else:
        return "muy débil"


def _classify_distribution_shape(skewness: float, kurtosis: float) -> str:
    """Classify distribution shape based on skewness and kurtosis"""
    if abs(skewness) < 0.5 and abs(kurtosis) < 3:
        return "aproximadamente normal"
    elif skewness > 1:
        return "sesgada hacia la derecha"
    elif skewness < -1:
        return "sesgada hacia la izquierda"
    elif kurtosis > 3:
        return "leptocúrtica (cola pesada)"
    elif kurtosis < 3:
        return "platocúrtica (cola ligera)"
    else:
        return "forma irregular"


def _create_histogram_data(
    values: List, bins: int, min_val: float, max_val: float
) -> Dict[str, Any]:
    """Create histogram data for visualization"""
    try:
        hist, bin_edges = get_numpy().histogram(
            [v for v in values if v is not None], bins=bins, range=(min_val, max_val)
        )

        return {
            "bins": bins,
            "counts": hist.tolist(),
            "bin_edges": bin_edges.tolist(),
            "total_values": len(values),
        }
    except Exception:
        return {"error": "Could not create histogram"}


def _generate_insights(
    df, analysis_result: Dict[str, Any], analysis_type: str
) -> List[str]:
    """Generate specific, actionable insights based on analysis results"""
    insights = []

    try:
        # Only generate truly actionable insights with specific numbers
        if analysis_type == "trends":
            trend_summary = analysis_result.get("trend_summary", {})
            growing_metrics = trend_summary.get("growing_metrics", [])
            declining_metrics = trend_summary.get("declining_metrics", [])
            seasonal_patterns = trend_summary.get("seasonal_patterns_detected", [])
            high_volatility = trend_summary.get("high_volatility_metrics", [])

            # Specific trend insights with numeric evidence (prefer explicit evidence string)
            for metric in growing_metrics:
                try:
                    name = (
                        metric.get("metric")
                        if isinstance(metric, dict)
                        else str(metric)
                    )
                    evidence = (
                        metric.get("trend_evidence")
                        if isinstance(metric, dict)
                        else None
                    )
                    mom = (
                        metric.get("avg_mom_pct") if isinstance(metric, dict) else None
                    )
                    if evidence:
                        insights.append(f"📈 {name}: {evidence}")
                    elif mom is not None:
                        insights.append(f"📈 {name}: MoM prom {float(mom):+,.1f}%")
                except Exception:
                    continue

            for metric in declining_metrics:
                try:
                    name = (
                        metric.get("metric")
                        if isinstance(metric, dict)
                        else str(metric)
                    )
                    evidence = (
                        metric.get("trend_evidence")
                        if isinstance(metric, dict)
                        else None
                    )
                    mom = (
                        metric.get("avg_mom_pct") if isinstance(metric, dict) else None
                    )
                    if evidence:
                        insights.append(f"📉 {name}: {evidence}")
                    elif mom is not None:
                        insights.append(f"📉 {name}: MoM prom {float(mom):+,.1f}%")
                except Exception:
                    continue

            # Specific seasonality insights with thresholds
            for pattern in seasonal_patterns:
                insights.append(
                    f"🗓️ {pattern['metric']}: Estacionalidad {pattern['strength']} ({pattern['amplitude_pct']:.1f}% variación) - {pattern['pattern']}"
                )

            # Specific volatility warnings
            for vol_metric in high_volatility:
                try:
                    v = (
                        vol_metric.get("volatility_pct")
                        if isinstance(vol_metric, dict)
                        else None
                    )
                    name = (
                        vol_metric.get("metric")
                        if isinstance(vol_metric, dict)
                        else str(vol_metric)
                    )
                    insights.append(
                        f"⚡ {name}: Volatilidad {vol_metric['risk_level'].lower()} ({float(v):.1f}%)"
                    )
                except Exception:
                    continue

        elif analysis_type == "performance":
            perf_summary = analysis_result.get("performance_summary", {})
            outlier_analysis = perf_summary.get("outlier_analysis", {})
            gaps = perf_summary.get("performance_gaps", {})

            total_outliers = outlier_analysis.get("total_outliers", 0)
            if total_outliers > df.height * 0.1:  # More than 10%
                insights.append(
                    f"⚡ {total_outliers} valores atípicos ({total_outliers / df.height * 100:.1f}% del dataset)"
                )

            critical_gaps = gaps.get("critical_gaps", [])
            for gap in critical_gaps[:2]:  # Only show top 2
                insights.append(
                    f"📊 {gap['analysis']}: Brecha crítica de {abs(gap['gap_pct']):.0f}%"
                )

        elif analysis_type == "relationships":
            rel_summary = analysis_result.get("relationship_summary", {})
            strong_relationships = rel_summary.get("strong_relationships", 0)
            if strong_relationships > 0:
                correlations = analysis_result.get("correlations", {}).get(
                    "significant_correlations", []
                )
                top_corr = (
                    max(correlations, key=lambda x: abs(x.get("correlation", 0)))
                    if correlations
                    else None
                )
                if top_corr:
                    insights.append(
                        f"🔗 Correlación más fuerte: {top_corr['variables']} ({top_corr['correlation']:+.2f})"
                    )

        elif analysis_type == "overview":
            desc_stats = analysis_result.get("descriptive_stats", {})
            quality = analysis_result.get("data_quality", {})
            issues = quality.get("issues_found", 0)

            if issues > 0:
                quality_metrics = quality.get("quality_metrics", {})
                high_null_cols = quality_metrics.get("high_null_columns", [])
                if high_null_cols:
                    worst_null = max(high_null_cols, key=lambda x: x.get("null_pct", 0))
                    insights.append(
                        f"⚠️ {worst_null['column']}: {worst_null['null_pct']:.1f}% valores nulos"
                    )

    except Exception:
        pass

    # Return empty list if no specific insights - don't waste tokens on generic messages
    return insights


def _generate_recommendations(
    df, analysis_result: Dict[str, Any], analysis_type: str
) -> List[str]:
    """Generate specific, actionable recommendations with concrete next steps"""
    recommendations = []

    try:
        if analysis_type == "trends":
            trend_summary = analysis_result.get("trend_summary", {})
            declining_metrics = trend_summary.get("declining_metrics", [])
            high_volatility = trend_summary.get("high_volatility_metrics", [])

            # Specific recommendations for declining metrics
            for metric in declining_metrics:
                if (
                    metric.get("avg_mom_pct") and metric["avg_mom_pct"] < -5
                ):  # More than 5% monthly decline
                    recommendations.append(
                        f"🚨 {metric['metric']}: Implementar plan de recuperación (declive {metric['avg_mom_pct']:.1f}% mensual)"
                    )

            # Specific recommendations for volatility
            for vol_metric in high_volatility:
                if vol_metric.get("volatility_pct", 0) > 50:  # More than 50% volatility
                    recommendations.append(
                        f"⚖️ {vol_metric['metric']}: Investigar causas de volatilidad extrema ({vol_metric['volatility_pct']:.0f}%)"
                    )

        elif analysis_type == "performance":
            perf_summary = analysis_result.get("performance_summary", {})
            gaps = perf_summary.get("performance_gaps", {})
            critical_gaps = gaps.get("critical_gaps", [])

            # Specific gap recommendations
            for gap in critical_gaps[:2]:  # Top 2 critical gaps only
                recommendations.append(
                    f"🎯 {gap['analysis'].split('_by_')[0]}: Reducir brecha de {abs(gap['gap_pct']):.0f}% entre top y bottom performers"
                )

        elif analysis_type == "relationships":
            rel_summary = analysis_result.get("relationship_summary", {})
            if rel_summary.get("strong_relationships", 0) > 2:
                recommendations.append(
                    "📈 Construir modelo predictivo usando las 3+ correlaciones fuertes identificadas"
                )

        elif analysis_type == "overview":
            quality = analysis_result.get("data_quality", {})
            quality_metrics = quality.get("quality_metrics", {})
            high_null_cols = quality_metrics.get("high_null_columns", [])

            # Specific data quality recommendations
            for col_info in high_null_cols[:2]:  # Top 2 only
                if col_info.get("null_pct", 0) > 20:
                    recommendations.append(
                        f"🔧 {col_info['column']}: Implementar estrategia de imputación ({col_info['null_pct']:.1f}% nulos)"
                    )

    except Exception:
        pass

    # Return empty list if no actionable recommendations - don't waste tokens
    return recommendations


def _flexible_table_parser(data: str):
    """Flexible fallback parser for various table formats"""
    from utils.logger import logger

    try:
        # Split into lines and clean
        lines = [line.strip() for line in data.split("\n") if line.strip()]

        if not lines:
            return None

        # Look for any line that looks like headers (contains letters and separators)
        header_candidates = []
        for i, line in enumerate(lines):
            # Skip obvious separator lines
            if re.match(r"^[\s\|\-:]+$", line):
                continue

            # Check if line could be headers
            if "|" in line:
                parts = [p.strip() for p in line.strip("|").split("|") if p.strip()]
                if parts and any(re.search(r"[a-zA-Z]", p) for p in parts):
                    header_candidates.append((i, parts))

        if not header_candidates:
            logger.debug("No suitable headers found in flexible parser")
            return None

        # Use the first suitable header
        header_idx, headers = header_candidates[0]
        logger.debug(f"Found headers at line {header_idx}: {headers}")

        # Collect data rows after the header
        data_rows = []
        for i in range(header_idx + 1, len(lines)):
            line = lines[i]

            # Skip separator lines
            if re.match(r"^[\s\|\-:]+$", line):
                continue

            if "|" in line:
                parts = [p.strip() for p in line.strip("|").split("|")]

                # Handle pandas index column (first column often numeric index)
                if parts and parts[0].isdigit():
                    parts = parts[1:]  # Skip index column

                # Align with headers
                while len(parts) < len(headers):
                    parts.append("")
                parts = parts[: len(headers)]

                if any(p for p in parts):  # Only add non-empty rows
                    data_rows.append(parts)

        if not data_rows:
            logger.debug("No data rows found in flexible parser")
            return None

        logger.debug(
            f"Flexible parser found {len(data_rows)} data rows with {len(headers)} columns"
        )

        # Create DataFrame
        pl = get_polars()
        df = pl.DataFrame(data_rows, schema=headers, orient="row")
        return _infer_column_types(df)

    except Exception as e:
        logger.error(f"Flexible parser failed: {str(e)}")
        return None


# NEW COMPOSITE ANALYSIS FUNCTIONS
def _overview_analysis(
    df,
    target_columns: List[str],
    percentiles: List[float],
    statistical_tests: bool,
    confidence_level: float,
) -> Dict[str, Any]:
    """Comprehensive overview combining descriptive stats and distribution analysis"""

    results = {
        "summary": {
            "total_rows": df.height,
            "total_columns": len(target_columns),
            "numeric_columns_analyzed": len(
                [col for col in target_columns if col in df.columns]
            ),
            "dataset_size_category": (
                "Large"
                if df.height > 1000
                else "Medium"
                if df.height > 100
                else "Small"
                if df.height > 10
                else "Very Small"
            ),
        }
    }

    # Enhanced descriptive statistics with all requested measures
    desc_results = _descriptive_analysis(
        df, target_columns, percentiles, statistical_tests, confidence_level
    )
    results["descriptive_stats"] = desc_results

    # Distribution analysis
    dist_results = _distribution_analysis(df, target_columns, percentiles)
    results["distributions"] = dist_results

    # Totals for business metrics (exclude temporal columns like year/month)
    try:
        temporal_names = {"anio", "mes", "year", "month"}
        business_totals: Dict[str, float] = {}
        for col in target_columns:
            if (
                col in df.columns
                and col
                and col.strip()
                and col.lower() not in temporal_names
            ):
                if df[col].dtype in [pl.Int64, pl.Float64, pl.Int32, pl.Float32]:
                    try:
                        s = df[col].sum()
                        business_totals[col] = float(s) if s is not None else 0.0
                    except Exception:
                        continue
        if business_totals:
            results["business_totals"] = business_totals
    except Exception:
        # Safe fallback: ignore totals if any error occurs
        pass

    # Cross-column statistical summary
    cross_column_stats = {
        "columns_analyzed": len([col for col in target_columns if col in desc_results]),
        "statistical_summary": {},
    }

    if desc_results:
        # Aggregate statistics across all numeric columns
        all_means = [
            col_stats.get("mean", 0)
            for col_stats in desc_results.values()
            if isinstance(col_stats, dict) and col_stats.get("mean")
        ]
        all_stds = [
            col_stats.get("std", 0)
            for col_stats in desc_results.values()
            if isinstance(col_stats, dict) and col_stats.get("std")
        ]
        all_cvs = [
            col_stats.get("coefficient_of_variation", 0)
            for col_stats in desc_results.values()
            if isinstance(col_stats, dict) and col_stats.get("coefficient_of_variation")
        ]
        all_skew = [
            col_stats.get("skewness", 0)
            for col_stats in desc_results.values()
            if isinstance(col_stats, dict) and "skewness" in col_stats
        ]
        all_kurt = [
            col_stats.get("kurtosis", 0)
            for col_stats in desc_results.values()
            if isinstance(col_stats, dict) and "kurtosis" in col_stats
        ]

        if all_means:
            cross_column_stats["statistical_summary"] = {
                "mean_of_means": float(get_numpy().mean(all_means)),
                "avg_standard_deviation": float(get_numpy().mean(all_stds))
                if all_stds
                else 0,
                "avg_coefficient_of_variation": float(get_numpy().mean(all_cvs))
                if all_cvs
                else 0,
                "avg_skewness": float(get_numpy().mean(all_skew)) if all_skew else 0,
                "avg_kurtosis": float(get_numpy().mean(all_kurt)) if all_kurt else 0,
                "most_variable_column": max(
                    desc_results.items(),
                    key=lambda x: x[1].get("coefficient_of_variation", 0)
                    if isinstance(x[1], dict)
                    else 0,
                )[0]
                if desc_results
                else None,
                "most_stable_column": min(
                    desc_results.items(),
                    key=lambda x: x[1].get("coefficient_of_variation", float("inf"))
                    if isinstance(x[1], dict)
                    else float("inf"),
                )[0]
                if desc_results
                else None,
            }

    results["cross_column_analysis"] = cross_column_stats

    # Enhanced data quality summary
    quality_issues = []
    quality_metrics = {
        "high_null_columns": [],
        "high_variability_columns": [],
        "low_variability_columns": [],
        "skewed_columns": [],
        "outlier_prone_columns": [],
    }

    for col in target_columns:
        if col in desc_results:
            col_stats = desc_results[col]

            # Null percentage check
            null_pct = col_stats.get("null_percentage", 0)
            if null_pct > 10:
                quality_issues.append(f"{col}: {null_pct:.1f}% valores nulos")
                quality_metrics["high_null_columns"].append(
                    {"column": col, "null_pct": null_pct}
                )

            # Coefficient of variation check
            cv = col_stats.get("coefficient_of_variation", 0)
            if cv and cv > 1.5:
                quality_issues.append(f"{col}: Alta variabilidad (CV={cv:.2f})")
                quality_metrics["high_variability_columns"].append(
                    {"column": col, "cv": cv}
                )
            elif cv and cv < 0.05:
                quality_metrics["low_variability_columns"].append(
                    {"column": col, "cv": cv}
                )

            # Skewness check
            skewness = col_stats.get("skewness", 0)
            if abs(skewness) > 1.5:
                quality_issues.append(
                    f"{col}: Distribución muy sesgada (skew={skewness:.2f})"
                )
                quality_metrics["skewed_columns"].append(
                    {"column": col, "skewness": skewness}
                )

            # Outlier potential based on IQR
            q1 = col_stats.get("q1", 0)
            q3 = col_stats.get("q3", 0)
            iqr = col_stats.get("iqr", 0)
            range_val = col_stats.get("range", 0)
            if iqr > 0 and range_val > 0 and (range_val / iqr) > 6:
                quality_metrics["outlier_prone_columns"].append(
                    {"column": col, "range_to_iqr_ratio": range_val / iqr}
                )

    results["data_quality"] = {
        "issues_found": len(quality_issues),
        "issues": quality_issues,  # All issues
        "quality_metrics": quality_metrics,
    }

    # Statistical insights
    statistical_insights = []

    # Column-specific insights
    for col, col_stats in desc_results.items():
        if not isinstance(col_stats, dict):
            continue

        mean_val = col_stats.get("mean", 0)
        median_val = col_stats.get("median", 0)
        mode_val = col_stats.get("mode", None)

        # Central tendency comparison
        if mean_val and median_val:
            mean_median_diff = abs(mean_val - median_val) / median_val * 100
            if mean_median_diff > 20:
                statistical_insights.append(
                    f"{col}: Diferencia significativa entre media ({mean_val:.2f}) y mediana ({median_val:.2f})"
                )

        # Mode vs mean comparison
        if mode_val is not None and mean_val:
            mode_mean_diff = abs(mode_val - mean_val) / mean_val * 100
            if mode_mean_diff > 30:
                statistical_insights.append(
                    f"{col}: Moda ({mode_val}) difiere considerablemente de la media ({mean_val:.2f})"
                )

        # Distribution shape insights
        skewness = col_stats.get("skewness", 0)
        kurtosis = col_stats.get("kurtosis", 0)

        if abs(skewness) > 2:
            direction = "derecha" if skewness > 0 else "izquierda"
            statistical_insights.append(
                f"{col}: Distribución fuertemente sesgada hacia la {direction}"
            )

        if kurtosis > 3:
            statistical_insights.append(
                f"{col}: Distribución leptocúrtica (colas pesadas)"
            )
        elif kurtosis < -1:
            statistical_insights.append(
                f"{col}: Distribución platocúrtica (colas ligeras)"
            )

        # Quartile insights
        q1 = col_stats.get("q1", 0)
        q2 = median_val
        q3 = col_stats.get("q3", 0)

        if q1 and q2 and q3:
            lower_spread = q2 - q1
            upper_spread = q3 - q2
            if upper_spread > 2 * lower_spread:
                statistical_insights.append(
                    f"{col}: Distribución asimétrica - mayor dispersión en el rango superior"
                )
            elif lower_spread > 2 * upper_spread:
                statistical_insights.append(
                    f"{col}: Distribución asimétrica - mayor dispersión en el rango inferior"
                )

    results["statistical_insights"] = statistical_insights  # All insights

    return results


def _performance_analysis(
    df,
    target_columns: List[str],
    group_by_columns: Optional[List[str]],
    aggregation_method: str,
    outlier_method: str,
    outlier_threshold: float,
    top_n: int = 10,
    **kwargs,
) -> Dict[str, Any]:
    """Comprehensive performance analysis combining rankings, comparisons, outliers, and performance metrics"""

    results = {
        "analysis_overview": {
            "dataset_size": df.height,
            "columns_analyzed": len(target_columns),
            "grouping_columns": len(group_by_columns) if group_by_columns else 0,
            "analysis_method": aggregation_method,
            "outlier_detection": f"{outlier_method} (threshold: {outlier_threshold})",
        }
    }

    # Enhanced Rankings Analysis with detailed statistics
    ranking_results = _ranking_analysis(
        df, target_columns, group_by_columns, aggregation_method, top_n
    )

    # Add ranking insights and performance spreads
    enhanced_rankings = {}
    for col, ranking_info in ranking_results.items():
        if isinstance(ranking_info, dict):
            enhanced_rankings[col] = ranking_info.copy()

            # Add performance spread analysis
            top_performers = ranking_info.get("top_performers", [])
            bottom_performers = ranking_info.get("bottom_performers", [])

            if top_performers and bottom_performers:
                top_values = [p.get(col, 0) for p in top_performers]
                bottom_values = [p.get(col, 0) for p in bottom_performers]

                # Performance concentration analysis
                np = get_numpy()
                top_mean = np.mean(top_values) if top_values else 0
                bottom_mean = np.mean(bottom_values) if bottom_values else 0
                overall_mean = float(df[col].mean()) if df[col].mean() else 0

                enhanced_rankings[col]["performance_concentration"] = {
                    "top_performers_mean": top_mean,
                    "bottom_performers_mean": bottom_mean,
                    "overall_mean": overall_mean,
                    "top_vs_overall_ratio": top_mean / overall_mean
                    if overall_mean != 0
                    else 0,
                    "performance_spread_ratio": top_mean / bottom_mean
                    if bottom_mean != 0
                    else float("inf"),
                }

                # Performance distribution analysis
                col_std = float(df[col].std()) if df[col].std() else 0
                enhanced_rankings[col]["performance_distribution"] = {
                    "coefficient_of_variation": col_std / overall_mean
                    if overall_mean != 0
                    else 0,
                    "performance_inequality": "High"
                    if top_mean / bottom_mean > 3
                    else "Medium"
                    if top_mean / bottom_mean > 1.5
                    else "Low",
                }

    results["rankings"] = enhanced_rankings

    # Enhanced Comparative Analysis with statistical significance
    comparative_results = {}
    if group_by_columns:
        comp_results = _comparative_analysis(
            df, target_columns, group_by_columns, aggregation_method, True
        )  # Enable statistical tests

        # Add enhanced comparative insights
        for analysis_name, data in comp_results.items():
            if isinstance(data, dict) and "groups" in data:
                enhanced_comp = data.copy()
                groups = data.get("groups", [])

                if len(groups) >= 2:
                    # Calculate additional performance metrics
                    group_values = [g.get("mean", 0) for g in groups if g.get("mean")]
                    if group_values:
                        enhanced_comp["group_performance_analysis"] = {
                            "mean_performance": float(np.mean(group_values)),
                            "std_performance": float(np.std(group_values)),
                            "cv_across_groups": float(
                                np.std(group_values) / np.mean(group_values)
                            )
                            if np.mean(group_values) != 0
                            else 0,
                            "performance_range": max(group_values) - min(group_values),
                            "top_group_advantage": (
                                max(group_values) - np.mean(group_values)
                            )
                            / np.mean(group_values)
                            * 100
                            if np.mean(group_values) != 0
                            else 0,
                        }

                    # Group dominance analysis
                    total_value = sum(g.get("value", 0) for g in groups)
                    if total_value > 0:
                        top_performers_share = (
                            sum(
                                g.get("value", 0) for g in groups[: min(3, len(groups))]
                            )
                            / total_value
                            * 100
                            if len(groups) >= 3
                            else sum(g.get("value", 0) for g in groups)
                            / total_value
                            * 100
                        )
                        enhanced_comp["dominance_analysis"] = {
                            "top_performers_market_share": top_performers_share,
                            "market_concentration": "High"
                            if top_performers_share > 70
                            else "Medium"
                            if top_performers_share > 50
                            else "Low",
                            "hhi_index": sum(
                                (g.get("percentage_of_total", 0)) ** 2 for g in groups
                            ),  # Herfindahl-Hirschman Index
                        }

                comparative_results[analysis_name] = enhanced_comp

        results["comparisons"] = comparative_results

    # Enhanced Outlier Analysis with impact assessment
    outlier_results = _outlier_analysis(
        df, target_columns, outlier_method, outlier_threshold
    )
    enhanced_outliers = {}

    for col, outlier_info in outlier_results.items():
        if isinstance(outlier_info, dict):
            enhanced_outliers[col] = outlier_info.copy()

            # Add outlier impact analysis
            outlier_values = outlier_info.get("outlier_values", [])
            if outlier_values:
                col_mean = float(df[col].mean()) if df[col].mean() else 0
                col_median = float(df[col].median()) if df[col].median() else 0

                # Calculate outlier impact on statistics
                outlier_mean = np.mean(outlier_values)
                outlier_distance = abs(outlier_mean - col_mean)

                enhanced_outliers[col]["outlier_impact"] = {
                    "mean_outlier_value": outlier_mean,
                    "distance_from_mean": outlier_distance,
                    "impact_magnitude": outlier_distance / col_mean * 100
                    if col_mean != 0
                    else 0,
                    "outlier_type": "Upper" if outlier_mean > col_median else "Lower",
                    "severity": "Extreme"
                    if len(outlier_values) > df.height * 0.1
                    else "Moderate"
                    if len(outlier_values) > df.height * 0.05
                    else "Minor",
                }

    results["outliers"] = enhanced_outliers

    # Comprehensive Performance Summary
    perf_summary = {
        "outlier_analysis": {
            "total_outliers": sum(
                col_stats.get("outliers_count", 0)
                for col_stats in enhanced_outliers.values()
                if isinstance(col_stats, dict)
            ),
            "columns_with_outliers": len(
                [
                    col
                    for col, col_stats in enhanced_outliers.items()
                    if isinstance(col_stats, dict)
                    and col_stats.get("outliers_count", 0) > 0
                ]
            ),
            "severe_outlier_columns": len(
                [
                    col
                    for col, col_stats in enhanced_outliers.items()
                    if isinstance(col_stats, dict)
                    and col_stats.get("outlier_impact", {}).get("severity") == "Extreme"
                ]
            ),
        }
    }

    # Performance gaps analysis
    if comparative_results:
        large_gaps = []
        market_concentration_issues = []

        for analysis_name, data in comparative_results.items():
            if isinstance(data, dict):
                gap = data.get("performance_gap_pct", 0)
                if abs(gap) > 30:
                    large_gaps.append(
                        {
                            "analysis": analysis_name,
                            "gap_pct": gap,
                            "severity": "Critical"
                            if abs(gap) > 100
                            else "High"
                            if abs(gap) > 50
                            else "Moderate",
                        }
                    )

                # Check for market concentration issues
                dominance = data.get("dominance_analysis", {})
                concentration = dominance.get("market_concentration", "Low")
                if concentration == "High":
                    market_concentration_issues.append(
                        {
                            "analysis": analysis_name,
                            "concentration_level": concentration,
                            "top_3_share": dominance.get("top_3_market_share", 0),
                        }
                    )

        perf_summary["performance_gaps"] = {
            "significant_gaps_found": len(large_gaps),
            "critical_gaps": [g for g in large_gaps if g.get("severity") == "Critical"],
            "largest_gaps": sorted(
                large_gaps, key=lambda x: abs(x.get("gap_pct", 0)), reverse=True
            ),  # All gaps, sorted by severity
        }

        perf_summary["market_concentration"] = {
            "high_concentration_areas": len(market_concentration_issues),
            "concentration_details": market_concentration_issues,  # All concentration issues
        }

    # Performance efficiency metrics
    efficiency_metrics = {}
    for col in target_columns:
        if col in df.columns:
            col_data = df[col].drop_nulls()
            if len(col_data) > 0:
                values = col_data.to_list()

                # Calculate efficiency-related metrics
                q75 = np.percentile(values, 75)
                q25 = np.percentile(values, 25)
                median_val = np.median(values)

                efficiency_metrics[col] = {
                    "performance_spread": q75 - q25,
                    "upper_potential": q75 - median_val,
                    "improvement_opportunity": (q75 - q25) / median_val * 100
                    if median_val != 0
                    else 0,
                    "consistency_score": 1 / (1 + (q75 - q25) / median_val)
                    if median_val != 0
                    else 0,
                }

    perf_summary["efficiency_metrics"] = efficiency_metrics

    # Overall performance health score
    health_score = 100
    health_factors = []

    # Deduct points for issues
    total_outliers = perf_summary["outlier_analysis"]["total_outliers"]
    if total_outliers > df.height * 0.1:  # More than 10% outliers
        health_score -= 20
        health_factors.append("High outlier rate")
    elif total_outliers > df.height * 0.05:  # More than 5% outliers
        health_score -= 10
        health_factors.append("Moderate outlier rate")

    if "performance_gaps" in perf_summary:
        critical_gaps = len(perf_summary["performance_gaps"].get("critical_gaps", []))
        if critical_gaps > 0:
            health_score -= critical_gaps * 15
            health_factors.append(f"{critical_gaps} critical performance gaps")

    if "market_concentration" in perf_summary:
        high_concentration = perf_summary["market_concentration"][
            "high_concentration_areas"
        ]
        if high_concentration > 0:
            health_score -= high_concentration * 10
            health_factors.append(f"{high_concentration} high concentration areas")

    # Ensure health score doesn't go below 0
    health_score = max(0, health_score)

    perf_summary["performance_health"] = {
        "overall_score": health_score,
        "health_level": "Excellent"
        if health_score >= 90
        else "Good"
        if health_score >= 75
        else "Fair"
        if health_score >= 60
        else "Poor",
        "health_factors": health_factors,
        "recommendation_priority": "Low"
        if health_score >= 80
        else "Medium"
        if health_score >= 60
        else "High",
    }

    results["performance_summary"] = perf_summary

    return results


def _trends_analysis(
    df,
    target_columns: List[str],
    group_by_columns: Optional[List[str]],
    time_column: Optional[str],
    window_size: int,
    trend_periods: int,
    aggregation_method: str,
) -> Dict[str, Any]:
    """Enhanced temporal analysis with forecasting indicators and proper grouping support"""

    # Core temporal analysis
    temporal_results = _temporal_analysis(
        df, target_columns, time_column, window_size, trend_periods, aggregation_method
    )

    # Enhanced trend summary with specific criteria and actionable metrics
    trend_summary = {
        "growing_metrics": [],
        "declining_metrics": [],
        "stable_metrics": [],
        "high_volatility_metrics": [],
        "seasonal_patterns_detected": [],
    }

    for col, trend_info in temporal_results.items():
        if (
            isinstance(trend_info, dict) and col.strip()
        ):  # Filter out empty column names
            # Use actual MoM/YoY data for trend determination instead of slope
            avg_mom = trend_info.get("avg_mom_change_pct")
            latest_yoy = trend_info.get("yoy_change_pct")

            # Determine trend based on actual data, not slope
            trend_direction = "estable"
            trend_metric = None

            if (
                avg_mom is not None and abs(avg_mom) >= 2
            ):  # 2% average monthly change threshold
                trend_direction = "creciente" if avg_mom > 0 else "decreciente"
                trend_metric = f"Promedio MoM: {avg_mom:+.1f}%"
            elif (
                latest_yoy is not None and abs(latest_yoy) >= 10
            ):  # 10% YoY change threshold
                trend_direction = "creciente" if latest_yoy > 0 else "decreciente"
                trend_metric = f"YoY: {latest_yoy:+.1f}%"

            # Store specific metrics instead of generic descriptions
            if trend_direction == "creciente":
                trend_summary["growing_metrics"].append(
                    {
                        "metric": col,
                        "trend_evidence": trend_metric,
                        "avg_mom_pct": avg_mom,
                        "latest_yoy_pct": latest_yoy,
                    }
                )
            elif trend_direction == "decreciente":
                trend_summary["declining_metrics"].append(
                    {
                        "metric": col,
                        "trend_evidence": trend_metric,
                        "avg_mom_pct": avg_mom,
                        "latest_yoy_pct": latest_yoy,
                    }
                )
            else:
                trend_summary["stable_metrics"].append(
                    {
                        "metric": col,
                        "avg_mom_pct": avg_mom,
                        "latest_yoy_pct": latest_yoy,
                    }
                )

            # Volatility with specific thresholds
            volatility = trend_info.get("volatility", 0)
            if volatility > 0.25:  # Specific 25% volatility threshold
                trend_summary["high_volatility_metrics"].append(
                    {
                        "metric": col,
                        "volatility_pct": volatility * 100,
                        "risk_level": "Alto" if volatility > 0.5 else "Moderado",
                    }
                )

            # Seasonality with specific thresholds and details
            seasonality_details = trend_info.get("seasonality_details")
            if seasonality_details:
                amplitude_ratio = seasonality_details.get("amplitude_ratio", 0)
                if amplitude_ratio >= 0.15:  # 15% amplitude threshold for seasonality
                    trend_summary["seasonal_patterns_detected"].append(
                        {
                            "metric": col,
                            "amplitude_pct": amplitude_ratio * 100,
                            "strength": trend_info.get(
                                "seasonality_strength", "moderada"
                            ),
                            "pattern": trend_info.get("seasonality_examples"),
                        }
                    )

    # Only generate forecasts for metrics with clear trends
    forecasts = {}
    forecast_indicators = {}

    # Filter out empty column names and only forecast trending metrics
    trending_metrics = [m["metric"] for m in trend_summary["growing_metrics"]] + [
        m["metric"] for m in trend_summary["declining_metrics"]
    ]

    for col in trending_metrics:
        if col in temporal_results:
            trend_info = temporal_results[col]
            slope = trend_info.get("trend_slope", 0)
            volatility = trend_info.get("volatility", 0)

            # Only forecast if we have reasonable confidence
            if abs(slope) > 0.005 or trend_info.get("avg_mom_change_pct"):
                confidence = (
                    "alta"
                    if abs(slope) > 0.01 and volatility < 0.2
                    else "media"
                    if volatility < 0.4
                    else "baja"
                )
                forecast_periods = 3  # Fixed to 3 periods for consistency

                forecast_indicators[col] = {
                    "forecast_confidence": confidence,
                    "recommended_periods": forecast_periods,
                }

                # Generate forecasts
                if col in df.columns:
                    forecasted_values = _generate_forecasts(
                        df,
                        col,
                        slope,
                        volatility,
                        forecast_periods,
                        window_size,
                        time_column,
                        group_by_columns,
                    )
                    if forecasted_values:
                        forecasts[col] = forecasted_values

    return {
        "temporal_analysis": temporal_results,
        "trend_summary": trend_summary,
        "forecast_indicators": forecast_indicators,
        "forecasts": forecasts,
    }


def _generate_forecasts(
    df,
    col: str,
    slope: float,
    volatility: float,
    forecast_periods: int,
    window_size: int = 3,
    time_column: Optional[str] = None,
    group_by_columns: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Import and call the comprehensive forecasting function"""
    try:
        from .polars_forecasting import generate_forecasts

        return generate_forecasts(
            df,
            col,
            slope,
            volatility,
            forecast_periods,
            window_size,
            time_column,
            group_by_columns,
        )
    except ImportError:
        # Fallback to simple forecasting if the module is not available
        return _simple_forecast_fallback(df, col, slope, volatility, forecast_periods)


def _detect_period_unit(df, time_column: Optional[str] = None) -> str:
    """Detect the period unit from the DataFrame structure"""
    # Check for explicit time columns
    if "anio" in df.columns and "mes" in df.columns:
        return "mes"  # Monthly data
    elif "anio" in df.columns:
        return "año"  # Yearly data
    elif "mes" in df.columns:
        return "mes"  # Monthly data (single year)
    elif "trimestre" in df.columns or "quarter" in df.columns:
        return "trimestre"  # Quarterly data
    elif "semana" in df.columns or "week" in df.columns:
        return "semana"  # Weekly data
    elif "dia" in df.columns or "day" in df.columns:
        return "día"  # Daily data

    # Check actual time column if provided
    if time_column and time_column in df.columns:
        try:
            # Try to infer from time column data
            time_data = df[time_column].drop_nulls().to_list()
            if len(time_data) >= 2:
                # Check for date patterns or differences
                pl = get_polars()
                if df[time_column].dtype in [pl.Date, pl.Datetime]:
                    # Could analyze date differences, but for now default to período
                    return "período"
        except Exception:
            pass

    # Check for common time column names
    time_like_columns = [
        col
        for col in df.columns
        if any(
            keyword in col.lower()
            for keyword in ["fecha", "date", "time", "periodo", "period"]
        )
    ]
    if time_like_columns:
        return "período"  # Generic period

    # Default fallback
    return "período"


def _simple_forecast_fallback(
    df, col: str, slope: float, volatility: float, forecast_periods: int
) -> Dict[str, Any]:
    """Simple fallback forecast using trend extrapolation with clear explanations"""
    try:
        values = df[col].drop_nulls().to_list()
        if len(values) < 2:
            return {}

        last_value = values[-1]
        forecasts = []

        # Determine trend direction for explanations
        trend_direction = (
            "creciente" if slope > 0 else "decreciente" if slope < 0 else "estable"
        )
        trend_strength = (
            "fuerte"
            if abs(slope) > 0.02
            else "moderado"
            if abs(slope) > 0.005
            else "débil"
        )

        for i in range(1, forecast_periods + 1):
            # Simple trend extrapolation with exponential decay to handle uncertainty
            trend_component = slope * i * last_value
            decay_factor = 0.95**i  # Reduce confidence over time
            forecasted_value = last_value + (trend_component * decay_factor)
            forecasts.append(forecasted_value)

        # Calculate percentage changes for better understanding
        period_changes = []
        for i, forecast in enumerate(forecasts):
            if i == 0:
                change_pct = (
                    (forecast - last_value) / last_value * 100 if last_value != 0 else 0
                )
            else:
                change_pct = (
                    (forecast - forecasts[i - 1]) / forecasts[i - 1] * 100
                    if forecasts[i - 1] != 0
                    else 0
                )
            period_changes.append(change_pct)

        # Calculate proper confidence intervals based on historical volatility
        # Use 95% confidence interval (1.96 standard deviations for normal distribution)
        confidence_level = 0.95
        z_score = 1.96  # 95% confidence interval

        # Calculate confidence intervals that widen over time
        upper_bounds = []
        lower_bounds = []

        for i, forecast in enumerate(forecasts):
            # Standard error increases with forecast horizon
            time_factor = (i + 1) ** 0.5  # Square root of time for error propagation
            standard_error = volatility * last_value * time_factor

            margin_of_error = z_score * standard_error
            upper_bound = forecast + margin_of_error
            lower_bound = max(0, forecast - margin_of_error)  # Don't go below 0

            upper_bounds.append(upper_bound)
            lower_bounds.append(lower_bound)

        # Detect period unit from data structure
        period_unit = _detect_period_unit(df)

        # Enhanced explanations
        forecast_explanation = _generate_forecast_explanation(
            col,
            last_value,
            forecasts,
            trend_direction,
            trend_strength,
            volatility,
            forecast_periods,
            period_changes,
            period_unit,
        )

        return {
            "values": forecasts,
            "methods_used": ["simple_trend"],
            "upper_bounds": upper_bounds,
            "lower_bounds": lower_bounds,
            "periods": forecast_periods,
            "details": {"simple_trend": forecasts},
            "explanation": forecast_explanation,
            "period_changes_pct": period_changes,
            "confidence_intervals": {
                "explanation": "Los límites superior e inferior muestran el rango donde probablemente caerán los valores reales",
                "upper_bounds": upper_bounds,
                "lower_bounds": lower_bounds,
                "confidence_level": f"{confidence_level * 100:.0f}%",
                "statistical_interpretation": f"Hay un {confidence_level * 100:.0f}% de probabilidad de que los valores reales caigan dentro de estos rangos",
                "methodology": "Intervalos calculados usando distribución normal con factor de tiempo para propagación de error",
            },
        }
    except Exception:
        return {}


def _generate_forecast_explanation(
    column: str,
    last_value: float,
    forecasts: List[float],
    trend_direction: str,
    trend_strength: str,
    volatility: float,
    periods: int,
    period_changes: List[float],
) -> Dict[str, str]:
    """Generate user-friendly explanations for forecasts"""

    # Calculate total change
    total_change = forecasts[-1] - last_value if forecasts else 0
    total_change_pct = (total_change / last_value * 100) if last_value != 0 else 0

    # Average period change
    avg_period_change = (
        sum(period_changes) / len(period_changes) if period_changes else 0
    )

    explanations = {
        "resumen_ejecutivo": _generate_executive_summary(
            column,
            last_value,
            forecasts[-1] if forecasts else last_value,
            total_change_pct,
            trend_direction,
            periods,
        ),
        "metodologia": _generate_methodology_explanation(
            trend_direction, trend_strength, volatility
        ),
        "interpretacion_valores": _generate_value_interpretation(
            forecasts, last_value, period_changes
        ),
        "factores_clave": _generate_key_factors(
            trend_direction, trend_strength, volatility
        ),
        "recomendaciones_uso": _generate_usage_recommendations(
            volatility, trend_strength, periods
        ),
        "limitaciones": _generate_limitations_warning(volatility, periods),
    }

    return explanations


def _generate_executive_summary(
    column: str,
    current_value: float,
    final_forecast: float,
    total_change_pct: float,
    trend_direction: str,
    periods: int,
) -> str:
    """Generate executive summary of forecast"""

    direction_text = {
        "creciente": "aumentar",
        "decreciente": "disminuir",
        "estable": "mantenerse relativamente estable",
    }[trend_direction]

    change_magnitude = (
        "significativamente"
        if abs(total_change_pct) > 20
        else "moderadamente"
        if abs(total_change_pct) > 5
        else "ligeramente"
    )

    return f"📈 PRONÓSTICO PARA {column.upper()}: Basado en las tendencias actuales, se espera que {column} {direction_text} {change_magnitude} en los próximos {periods} períodos. El valor actual de {current_value:,.2f} podría llegar a {final_forecast:,.2f} (cambio del {total_change_pct:+.1f}%)."


def _generate_methodology_explanation(
    trend_direction: str, trend_strength: str, volatility: float
) -> str:
    """Explain the forecasting methodology"""

    volatility_desc = (
        "alta" if volatility > 0.3 else "moderada" if volatility > 0.15 else "baja"
    )

    return f"🔬 METODOLOGÍA: Este pronóstico utiliza extrapolación de tendencias basada en el patrón {trend_direction} {trend_strength} observado en los datos históricos. La volatilidad {volatility_desc} ({volatility:.1%}) se incorpora para crear intervalos de confianza realistas. El modelo ajusta la confianza hacia períodos futuros más lejanos."


def _generate_value_interpretation(
    forecasts: List[float],
    last_value: float,
    period_changes: List[float],
    upper_bounds: List[float] = None,
    lower_bounds: List[float] = None,
    confidence_level: str = None,
    period_unit: str = None,
) -> str:
    """Explain what the forecasted values mean including confidence intervals"""

    if not forecasts:
        return "No se pudieron generar pronósticos."

    next_period = forecasts[0]
    next_change = period_changes[0] if period_changes else 0

    avg_change = sum(period_changes) / len(period_changes) if period_changes else 0

    interpretation = f"📊 INTERPRETACIÓN DE VALORES:\n"

    # Define what "período" means in this context
    interpretation += f"📅 DEFINICIÓN DE PERÍODO: Un 'período' representa la siguiente unidad de tiempo en su serie de datos "
    interpretation += f"(mes, trimestre, año, etc.). Los pronósticos muestran valores esperados para cada período futuro consecutivo.\n\n"

    interpretation += (
        f"• Próximo período: {next_period:,.2f} ({next_change:+.1f}% vs. actual)\n"
    )

    # Add confidence interval for next period if available
    if (
        upper_bounds
        and lower_bounds
        and len(upper_bounds) > 0
        and len(lower_bounds) > 0
    ):
        next_upper = upper_bounds[0]
        next_lower = lower_bounds[0]
        interpretation += f"  └─ Rango probable: {next_lower:,.2f} - {next_upper:,.2f}"
        if confidence_level:
            interpretation += f" ({confidence_level} confianza)\n"
        else:
            interpretation += "\n"
        interpretation += f"  └─ Esto significa que el valor real del próximo período tiene una alta probabilidad de caer dentro de este rango\n"

    interpretation += f"• Cambio promedio por período: {avg_change:+.1f}%\n"
    interpretation += (
        f"• Valor final proyectado (período {len(forecasts)}): {forecasts[-1]:,.2f}\n"
    )

    # Add confidence interval for final period
    if upper_bounds and lower_bounds:
        final_upper = upper_bounds[-1]
        final_lower = lower_bounds[-1]
        interpretation += (
            f"  └─ Rango final probable: {final_lower:,.2f} - {final_upper:,.2f}\n"
        )
        interpretation += f"  └─ La incertidumbre aumenta con el tiempo, por eso el rango final es más amplio\n"

    if len(forecasts) > 1:
        max_value = max(forecasts)
        min_value = min(forecasts)
        interpretation += f"• Rango de valores centrales (todos los períodos): {min_value:,.2f} - {max_value:,.2f}\n"

    # Enhanced confidence interval explanation with proper statistical interpretation
    if upper_bounds and lower_bounds:
        # Calculate average margin of error as percentage
        avg_margin_pct = sum(
            abs(upper_bounds[i] - forecasts[i]) / forecasts[i] * 100
            for i in range(len(forecasts))
        ) / len(forecasts)

        interpretation += f"\n🎯 INTERVALOS DE CONFIANZA (EXPLICACIÓN ESTADÍSTICA):\n"
        interpretation += f"• Nivel de confianza: {confidence_level or '95%'} - esto es el estándar en análisis estadístico\n"
        interpretation += f"• Significa que hay un {confidence_level or '95%'} de probabilidad de que el valor real caiga dentro del rango\n"
        interpretation += f"• Margen de error promedio: ±{avg_margin_pct:.1f}% alrededor de los valores centrales\n"

        # Period-specific confidence intervals
        if period_unit:
            interpretation += f"• Próximo {period_unit}: {lower_bounds[0]:,.2f} - {upper_bounds[0]:,.2f} ({confidence_level or '95%'} confianza)\n"
            interpretation += f"• Final ({period_unit} {len(forecasts)}): {lower_bounds[-1]:,.2f} - {upper_bounds[-1]:,.2f}\n"
        else:
            interpretation += f"• Próximo período: {lower_bounds[0]:,.2f} - {upper_bounds[0]:,.2f} ({confidence_level or '95%'} confianza)\n"
            interpretation += (
                f"• Período final: {lower_bounds[-1]:,.2f} - {upper_bounds[-1]:,.2f}\n"
            )

        interpretation += f"• Los intervalos se amplían con el tiempo debido a la propagación natural del error\n"
        interpretation += f"• Use el valor central para planificación y los límites para análisis de riesgo"

    return interpretation


def _generate_key_factors(
    trend_direction: str, trend_strength: str, volatility: float
) -> str:
    """Explain key factors affecting the forecast"""

    factors = "🔑 FACTORES CLAVE QUE INFLUYEN EN EL PRONÓSTICO:\n"

    # Trend factor
    if trend_direction == "creciente":
        factors += (
            f"• ✅ Tendencia {trend_strength} al alza favorece crecimiento continuo\n"
        )
    elif trend_direction == "decreciente":
        factors += (
            f"• ⚠️ Tendencia {trend_strength} a la baja sugiere declive continuo\n"
        )
    else:
        factors += f"• 📊 Tendencia estable sugiere valores similares\n"

    # Volatility factor
    if volatility > 0.3:
        factors += f"• ⚡ Alta volatilidad ({volatility:.1%}) aumenta incertidumbre\n"
        factors += f"• 📈 Pueden ocurrir cambios bruscos inesperados"
    elif volatility > 0.15:
        factors += f"• 🎯 Volatilidad moderada ({volatility:.1%}) permite predicciones razonables\n"
        factors += f"• 📊 Cambios graduales son más probables"
    else:
        factors += (
            f"• ✅ Baja volatilidad ({volatility:.1%}) indica patrones predecibles\n"
        )
        factors += f"• 🎯 Alta confianza en la dirección de la tendencia"

    return factors


def _generate_usage_recommendations(
    volatility: float, trend_strength: str, periods: int
) -> str:
    """Generate recommendations for how to use the forecast"""

    recommendations = "💡 RECOMENDACIONES DE USO:\n"

    if volatility < 0.2 and trend_strength in ["fuerte", "moderado"]:
        recommendations += (
            "• ✅ Alta confiabilidad - úselo para planificación estratégica\n"
        )
        recommendations += "• 📈 Ideal para proyecciones de presupuesto y recursos\n"
    else:
        recommendations += "• ⚠️ Confiabilidad moderada - úselo como guía general\n"
        recommendations += "• 🔍 Combine con análisis cualitativos adicionales\n"

    if periods <= 3:
        recommendations += "• ⏱️ Pronóstico a corto plazo - mayor precisión esperada\n"
    else:
        recommendations += "• 📅 Pronóstico a largo plazo - revise periódicamente\n"

    recommendations += "• 📊 Monitoree los valores reales vs. pronósticos\n"
    recommendations += "• 🔄 Actualice el modelo con nuevos datos regularmente"

    return recommendations


def _generate_limitations_warning(volatility: float, periods: int) -> str:
    """Generate warnings about forecast limitations"""

    warnings = "⚠️ LIMITACIONES IMPORTANTES:\n"

    warnings += "• 📈 Asume que las tendencias pasadas continuarán\n"
    warnings += "• 🚫 No considera eventos externos o cambios estructurales\n"

    if volatility > 0.3:
        warnings += "• ⚡ Alta volatilidad reduce precisión de predicciones\n"

    if periods > 5:
        warnings += "• 📅 Pronósticos a largo plazo son menos confiables\n"

    warnings += "• 🎯 Los intervalos de confianza muestran incertidumbre\n"
    warnings += "• 🔍 Considere factores cualitativos no capturados por el modelo\n"
    warnings += "• ⏰ La precisión disminuye con el tiempo"

    return warnings


def _relationships_analysis(
    df, target_columns: List[str], correlation_threshold: float, **kwargs
) -> Dict[str, Any]:
    """Comprehensive relationship analysis combining correlations, regression, and dependency patterns"""

    results = {
        "analysis_overview": {
            "dataset_size": df.height,
            "variables_analyzed": len(target_columns),
            "correlation_threshold": correlation_threshold,
            "total_possible_pairs": len(target_columns)
            * (len(target_columns) - 1)
            // 2,
        }
    }

    if len(target_columns) < 2:
        return {"error": "Need at least 2 numeric columns for relationship analysis"}

    # Enhanced Correlation Analysis
    corr_results = _correlation_analysis(df, target_columns, correlation_threshold)

    # Add correlation strength distribution
    all_correlations = corr_results.get("correlations", {})
    correlation_strengths = [
        abs(c.get("correlation", 0))
        for c in all_correlations.values()
        if isinstance(c, dict) and "correlation" in c
    ]

    enhanced_correlations = corr_results.copy()
    if correlation_strengths:
        enhanced_correlations["correlation_distribution"] = {
            "mean_strength": float(np.mean(correlation_strengths)),
            "max_strength": float(np.max(correlation_strengths)),
            "min_strength": float(np.min(correlation_strengths)),
            "std_strength": float(np.std(correlation_strengths)),
            "very_strong_count": sum(1 for c in correlation_strengths if c >= 0.9),
            "strong_count": sum(1 for c in correlation_strengths if 0.7 <= c < 0.9),
            "moderate_count": sum(1 for c in correlation_strengths if 0.5 <= c < 0.7),
            "weak_count": sum(
                1 for c in correlation_strengths if correlation_threshold <= c < 0.5
            ),
        }

    results["correlations"] = enhanced_correlations

    # Advanced Regression Analysis
    significant_pairs = []
    if "significant_correlations" in corr_results:
        for corr in corr_results["significant_correlations"]:
            if abs(corr.get("correlation", 0)) > 0.3:
                vars_str = corr.get("variables", "")
                if " - " in vars_str:
                    var1, var2 = vars_str.split(" - ")
                    significant_pairs.append(
                        (var1.strip(), var2.strip(), abs(corr.get("correlation", 0)))
                    )

    # Sort by correlation strength
    significant_pairs.sort(key=lambda x: x[2], reverse=True)

    # Enhanced regression analysis
    regression_results = {}
    for i, (var1, var2, corr_strength) in enumerate(
        significant_pairs
    ):  # Process all significant relationships
        if var1 in target_columns and var2 in target_columns:
            # Bidirectional regression analysis
            reg_result1 = _regression_analysis(df, [var1, var2], target_variable=var2)
            reg_result2 = _regression_analysis(df, [var1, var2], target_variable=var1)

            # Enhanced regression with additional metrics
            enhanced_reg = {
                f"{var1}_predicts_{var2}": reg_result1,
                f"{var2}_predicts_{var1}": reg_result2,
                "relationship_metrics": {
                    "correlation_strength": corr_strength,
                    "bidirectional_r2_avg": (
                        reg_result1.get(f"{var1}_regression", {}).get("r_squared", 0)
                        + reg_result2.get(f"{var2}_regression", {}).get("r_squared", 0)
                    )
                    / 2
                    if isinstance(reg_result1, dict) and isinstance(reg_result2, dict)
                    else 0,
                    "relationship_type": "Strong bidirectional"
                    if corr_strength > 0.7
                    else "Moderate"
                    if corr_strength > 0.5
                    else "Weak",
                },
            }

            # Add linearity assessment
            try:
                x_vals = df[var1].drop_nulls().to_list()
                y_vals = df[var2].drop_nulls().to_list()

                if len(x_vals) >= len(y_vals):
                    x_vals = x_vals[: len(y_vals)]
                else:
                    y_vals = y_vals[: len(x_vals)]

                if len(x_vals) > 2 and len(y_vals) > 2:
                    # Calculate residuals for linearity assessment
                    from scipy.stats import pearsonr

                    linear_r, _ = pearsonr(x_vals, y_vals)

                    # Simple linearity check using correlation of squared residuals
                    enhanced_reg["relationship_metrics"]["linearity_score"] = abs(
                        linear_r
                    )
                    enhanced_reg["relationship_metrics"]["relationship_quality"] = (
                        "Excellent"
                        if abs(linear_r) > 0.9
                        else "Good"
                        if abs(linear_r) > 0.7
                        else "Fair"
                        if abs(linear_r) > 0.5
                        else "Poor"
                    )
            except Exception:
                enhanced_reg["relationship_metrics"]["linearity_score"] = corr_strength
                enhanced_reg["relationship_metrics"]["relationship_quality"] = "Unknown"

            regression_results[f"{var1}_vs_{var2}"] = enhanced_reg

    results["regressions"] = regression_results

    # Comprehensive Relationship Network Analysis
    network_analysis = {
        "nodes": len(target_columns),
        "edges": len(corr_results.get("significant_correlations", [])),
        "density": len(corr_results.get("significant_correlations", []))
        / results["analysis_overview"]["total_possible_pairs"]
        if results["analysis_overview"]["total_possible_pairs"] > 0
        else 0,
    }

    # Find the most connected variables (hubs)
    connection_count = {col: 0 for col in target_columns}
    connection_strengths = {col: [] for col in target_columns}

    for corr in corr_results.get("significant_correlations", []):
        vars_str = corr.get("variables", "")
        strength = abs(corr.get("correlation", 0))

        if " - " in vars_str:
            var1, var2 = vars_str.split(" - ")
            var1, var2 = var1.strip(), var2.strip()

            connection_count[var1] = connection_count.get(var1, 0) + 1
            connection_count[var2] = connection_count.get(var2, 0) + 1

            connection_strengths[var1].append(strength)
            connection_strengths[var2].append(strength)

    # Calculate hub metrics
    hub_variables = []
    for var in target_columns:
        connections = connection_count.get(var, 0)
        strengths = connection_strengths.get(var, [])

        if connections > 0:
            hub_variables.append(
                {
                    "variable": var,
                    "connections": connections,
                    "avg_connection_strength": float(np.mean(strengths)),
                    "max_connection_strength": float(np.max(strengths)),
                    "hub_importance": connections * float(np.mean(strengths)),
                    "hub_type": "Major"
                    if connections >= len(target_columns) * 0.5
                    else "Minor",
                }
            )

    hub_variables.sort(key=lambda x: x["hub_importance"], reverse=True)
    network_analysis["hub_variables"] = (
        hub_variables  # All hub variables, sorted by importance
    )

    # Relationship clusters (groups of highly correlated variables)
    relationship_clusters = _identify_relationship_clusters(
        target_columns, corr_results.get("significant_correlations", [])
    )
    network_analysis["clusters"] = relationship_clusters

    results["network_analysis"] = network_analysis

    # Advanced Relationship Patterns
    relationship_patterns = {
        "positive_relationships": len(
            [
                c
                for c in corr_results.get("significant_correlations", [])
                if c.get("correlation", 0) > 0
            ]
        ),
        "negative_relationships": len(
            [
                c
                for c in corr_results.get("significant_correlations", [])
                if c.get("correlation", 0) < 0
            ]
        ),
        "strong_positive": len(
            [
                c
                for c in corr_results.get("significant_correlations", [])
                if c.get("correlation", 0) > 0.7
            ]
        ),
        "strong_negative": len(
            [
                c
                for c in corr_results.get("significant_correlations", [])
                if c.get("correlation", 0) < -0.7
            ]
        ),
    }

    # Identify potential causal chains (A -> B -> C patterns)
    causal_chains = _identify_potential_causal_chains(
        target_columns, corr_results.get("significant_correlations", [])
    )
    relationship_patterns["potential_causal_chains"] = (
        causal_chains  # All potential causal chains
    )

    # Variable dependency analysis
    dependency_analysis = {}
    for var in target_columns:
        var_deps = []
        for corr in corr_results.get("significant_correlations", []):
            vars_str = corr.get("variables", "")
            if var in vars_str:
                other_var = vars_str.replace(var, "").replace(" - ", "").strip()
                if other_var:
                    var_deps.append(
                        {
                            "dependent_variable": other_var,
                            "strength": abs(corr.get("correlation", 0)),
                            "direction": "positive"
                            if corr.get("correlation", 0) > 0
                            else "negative",
                        }
                    )

        if var_deps:
            var_deps.sort(key=lambda x: x["strength"], reverse=True)
            dependency_analysis[var] = {
                "total_dependencies": len(var_deps),
                "strongest_dependencies": var_deps,  # All dependencies, sorted by strength
                "avg_dependency_strength": float(
                    np.mean([d["strength"] for d in var_deps])
                ),
                "dependency_type": "Highly connected"
                if len(var_deps) >= 3
                else "Moderately connected"
                if len(var_deps) >= 2
                else "Weakly connected",
            }

    relationship_patterns["dependency_analysis"] = dependency_analysis
    results["relationship_patterns"] = relationship_patterns

    # Comprehensive Relationship Summary
    relationship_summary = {
        "total_correlations_found": len(corr_results.get("correlations", {})),
        "significant_relationships": len(
            corr_results.get("significant_correlations", [])
        ),
        "strong_relationships": len(
            [
                c
                for c in corr_results.get("significant_correlations", [])
                if abs(c.get("correlation", 0)) > 0.7
            ]
        ),
        "potential_causal_candidates": len(regression_results),
        "network_connectivity": network_analysis["density"],
        "relationship_diversity": {
            "positive_ratio": relationship_patterns["positive_relationships"]
            / max(1, len(corr_results.get("significant_correlations", []))),
            "negative_ratio": relationship_patterns["negative_relationships"]
            / max(1, len(corr_results.get("significant_correlations", []))),
            "balance_score": 1
            - abs(
                relationship_patterns["positive_relationships"]
                - relationship_patterns["negative_relationships"]
            )
            / max(1, len(corr_results.get("significant_correlations", []))),
        },
    }

    # Relationship health score
    health_score = 50  # Start from neutral
    health_factors = []

    # Add points for good relationships
    if relationship_summary["network_connectivity"] > 0.5:
        health_score += 20
        health_factors.append("High network connectivity")
    elif relationship_summary["network_connectivity"] > 0.3:
        health_score += 10
        health_factors.append("Moderate network connectivity")

    if relationship_summary["strong_relationships"] > 0:
        health_score += min(20, relationship_summary["strong_relationships"] * 5)
        health_factors.append(
            f"{relationship_summary['strong_relationships']} strong relationships"
        )

    if relationship_summary["relationship_diversity"]["balance_score"] > 0.8:
        health_score += 10
        health_factors.append("Good positive/negative balance")

    # Deduct points for problems
    if relationship_summary["significant_relationships"] == 0:
        health_score -= 30
        health_factors.append("No significant relationships found")

    # Ensure score is within bounds
    health_score = max(0, min(100, health_score))

    relationship_summary["relationship_health"] = {
        "overall_score": health_score,
        "health_level": "Excellent"
        if health_score >= 80
        else "Good"
        if health_score >= 60
        else "Fair"
        if health_score >= 40
        else "Poor",
        "health_factors": health_factors,
        "recommendation_priority": "Low"
        if health_score >= 70
        else "Medium"
        if health_score >= 50
        else "High",
    }

    results["relationship_summary"] = relationship_summary

    return results


def _identify_relationship_clusters(
    variables: List[str], significant_correlations: List[Dict]
) -> List[Dict[str, Any]]:
    """Identify clusters of highly correlated variables"""
    clusters = []

    try:
        # Build adjacency list for strong relationships (>0.6)
        adjacency = {var: set() for var in variables}

        for corr in significant_correlations:
            if abs(corr.get("correlation", 0)) > 0.6:
                vars_str = corr.get("variables", "")
                if " - " in vars_str:
                    var1, var2 = vars_str.split(" - ")
                    var1, var2 = var1.strip(), var2.strip()
                    adjacency[var1].add(var2)
                    adjacency[var2].add(var1)

        # Find connected components (clusters)
        visited = set()
        for var in variables:
            if var not in visited:
                cluster = set()
                stack = [var]

                while stack:
                    current = stack.pop()
                    if current not in visited:
                        visited.add(current)
                        cluster.add(current)
                        stack.extend(adjacency[current] - visited)

                if len(cluster) > 1:  # Only include clusters with more than 1 variable
                    # Calculate cluster metrics
                    cluster_vars = list(cluster)
                    cluster_correlations = []

                    for corr in significant_correlations:
                        vars_str = corr.get("variables", "")
                        if " - " in vars_str:
                            var1, var2 = vars_str.split(" - ")
                            if var1.strip() in cluster and var2.strip() in cluster:
                                cluster_correlations.append(
                                    abs(corr.get("correlation", 0))
                                )

                    if cluster_correlations:
                        clusters.append(
                            {
                                "variables": cluster_vars,
                                "size": len(cluster_vars),
                                "avg_correlation": float(np.mean(cluster_correlations)),
                                "max_correlation": float(np.max(cluster_correlations)),
                                "min_correlation": float(np.min(cluster_correlations)),
                                "cluster_strength": "Strong"
                                if np.mean(cluster_correlations) > 0.7
                                else "Moderate",
                            }
                        )

    except Exception:
        pass  # Return empty list if clustering fails

    return sorted(clusters, key=lambda x: x["avg_correlation"], reverse=True)


def _identify_potential_causal_chains(
    variables: List[str], significant_correlations: List[Dict]
) -> List[Dict[str, Any]]:
    """Identify potential causal chains (A -> B -> C patterns)"""
    chains = []

    try:
        # Build correlation graph
        correlations = {}
        for corr in significant_correlations:
            vars_str = corr.get("variables", "")
            correlation_val = corr.get("correlation", 0)

            if (
                " - " in vars_str and abs(correlation_val) > 0.5
            ):  # Only consider moderate+ correlations
                var1, var2 = vars_str.split(" - ")
                var1, var2 = var1.strip(), var2.strip()
                correlations[(var1, var2)] = correlation_val
                correlations[(var2, var1)] = correlation_val

        # Look for potential causal chains
        for var_a in variables:
            for var_b in variables:
                if var_a != var_b and (var_a, var_b) in correlations:
                    for var_c in variables:
                        if (
                            var_c != var_a
                            and var_c != var_b
                            and (var_b, var_c) in correlations
                        ):
                            # Check if A-B-C forms a potential causal chain
                            corr_ab = correlations.get((var_a, var_b), 0)
                            corr_bc = correlations.get((var_b, var_c), 0)
                            corr_ac = correlations.get((var_a, var_c), 0)

                            # Causal chain heuristic: A-B and B-C correlations should be stronger than A-C
                            if abs(corr_ab) > 0.5 and abs(corr_bc) > 0.5:
                                chain_strength = (abs(corr_ab) + abs(corr_bc)) / 2

                                # Check if this creates a reasonable chain
                                if abs(corr_ac) < min(abs(corr_ab), abs(corr_bc)):
                                    chains.append(
                                        {
                                            "chain": f"{var_a} → {var_b} → {var_c}",
                                            "variables": [var_a, var_b, var_c],
                                            "chain_strength": chain_strength,
                                            "ab_correlation": corr_ab,
                                            "bc_correlation": corr_bc,
                                            "ac_correlation": corr_ac,
                                            "evidence_strength": "Strong"
                                            if chain_strength > 0.7
                                            else "Moderate"
                                            if chain_strength > 0.6
                                            else "Weak",
                                        }
                                    )

    except Exception:
        pass  # Return empty list if chain identification fails

    # Remove duplicates and sort by strength
    unique_chains = []
    seen_chains = set()

    for chain in sorted(chains, key=lambda x: x["chain_strength"], reverse=True):
        chain_key = tuple(sorted(chain["variables"]))
        if chain_key not in seen_chains:
            seen_chains.add(chain_key)
            unique_chains.append(chain)

    return unique_chains


def _analyze_per_product_trends(
    df,
    col: str,
    aggregation_method: str,
    year_col: str = "anio",
    month_col: str = "mes",
) -> Dict[str, Any]:
    """Analyze trends for individual products, identifying top 3 and bottom 3 performers

    Args:
        df: DataFrame with product data
        col: Value column to analyze
        aggregation_method: Method to aggregate data
        year_col: Year column name
        month_col: Month column name (optional, use None for yearly data)

    Returns:
        Dictionary with per-product trends analysis
    """
    try:
        # Auto-detect product column
        product_columns = []
        for column_name in df.columns:
            if df[column_name].dtype == pl.Utf8:
                unique_count = df[column_name].n_unique()
                col_lower = column_name.lower()
                is_product_name = any(
                    pattern in col_lower
                    for pattern in [
                        "producto",
                        "product",
                        "sku",
                        "item",
                        "articulo",
                        "codigo",
                    ]
                )
                reasonable_cardinality = 3 <= unique_count <= 100

                if is_product_name and reasonable_cardinality:
                    product_columns.append(column_name)

        if not product_columns:
            return {
                "error": "No suitable product column found for per-product analysis"
            }

        product_col = product_columns[0]  # Use the first suitable product column

        # Get aggregation expression
        agg_expr = _get_aggregation_expression(col, aggregation_method)

        # First, calculate total performance per product to identify top/bottom performers
        product_totals = (
            df.group_by(product_col)
            .agg([agg_expr.alias("total_value")])
            .sort("total_value", descending=True)
        )

        product_list = product_totals.to_dicts()
        if len(product_list) < 3:
            return {"error": "Not enough products for top/bottom 3 analysis"}

        # Identify top 3 and bottom 3
        top_3_products = [p[product_col] for p in product_list[:3]]
        bottom_3_products = [p[product_col] for p in product_list[-3:]]

        result = {
            "product_column_used": product_col,
            "total_products_analyzed": len(product_list),
            "top_3_products": {"products": top_3_products, "details": product_list[:3]},
            "bottom_3_products": {
                "products": bottom_3_products,
                "details": product_list[-3:],
            },
        }

        # Calculate trends for each product in top/bottom groups
        if month_col and month_col in df.columns:
            # Monthly trends analysis
            result["monthly_trends"] = {"top_3": {}, "bottom_3": {}}

            # Analyze top 3 products
            for product in top_3_products:
                product_data = df.filter(pl.col(product_col) == product)
                trends = _calculate_product_monthly_trends(
                    product_data, col, year_col, month_col, aggregation_method
                )
                if trends:
                    result["monthly_trends"]["top_3"][product] = trends

            # Analyze bottom 3 products
            for product in bottom_3_products:
                product_data = df.filter(pl.col(product_col) == product)
                trends = _calculate_product_monthly_trends(
                    product_data, col, year_col, month_col, aggregation_method
                )
                if trends:
                    result["monthly_trends"]["bottom_3"][product] = trends

        elif year_col and year_col in df.columns:
            # Yearly trends analysis
            result["yearly_trends"] = {"top_3": {}, "bottom_3": {}}

            # Analyze top 3 products
            for product in top_3_products:
                product_data = df.filter(pl.col(product_col) == product)
                trends = _calculate_product_yearly_trends(
                    product_data, col, year_col, aggregation_method
                )
                if trends:
                    result["yearly_trends"]["top_3"][product] = trends

            # Analyze bottom 3 products
            for product in bottom_3_products:
                product_data = df.filter(pl.col(product_col) == product)
                trends = _calculate_product_yearly_trends(
                    product_data, col, year_col, aggregation_method
                )
                if trends:
                    result["yearly_trends"]["bottom_3"][product] = trends

        # Add summary insights
        result["insights"] = _generate_per_product_insights(result)

        return result

    except Exception as e:
        return {"error": f"Per-product analysis failed: {str(e)}"}


def _calculate_product_monthly_trends(
    product_df, col: str, year_col: str, month_col: str, aggregation_method: str
) -> Optional[Dict[str, Any]]:
    """Calculate monthly trends for a specific product"""
    try:
        if product_df.height == 0:
            return None

        agg_expr = _get_aggregation_expression(col, aggregation_method)

        # Aggregate by year-month
        monthly = (
            product_df.select(
                [
                    pl.col(year_col).cast(pl.Int64),
                    pl.col(month_col).cast(pl.Int64),
                    pl.col(col),
                ]
            )
            .drop_nulls()
            .group_by([year_col, month_col])
            .agg([agg_expr.alias("value")])
            .sort([year_col, month_col])
        )

        rows = monthly.to_dicts()
        if len(rows) < 2:
            return None

        # Build ordered list
        ordered = [
            (int(r[year_col]), int(r[month_col]), r["value"])
            for r in rows
            if r.get("value") is not None
        ]
        val_map = {(y, m): v for (y, m, v) in ordered}
        years = sorted({y for (y, m, v) in ordered})
        months_by_year = {
            y: sorted({m for (yy, m, v) in ordered if yy == y}) for y in years
        }

        # Calculate MoM changes
        mom_series_by_year = {}
        for y in years:
            months = months_by_year.get(y, [])
            if len(months) >= 2:
                series = {}
                for i in range(1, len(months)):
                    m_curr = months[i]
                    m_prev = months[i - 1]
                    v_prev = val_map.get((y, m_prev))
                    v_curr = val_map.get((y, m_curr))
                    if v_prev not in (None, 0) and v_curr is not None:
                        try:
                            series[m_curr] = (v_curr - v_prev) / v_prev * 100
                        except Exception:
                            continue
                if series:
                    mom_series_by_year[y] = series

        # Calculate YoY changes
        yoy_series_by_year = {}
        for idx in range(1, len(years)):
            y = years[idx]
            prev = years[idx - 1]
            series = {}
            for m in months_by_year.get(y, []):
                v_cur = val_map.get((y, m))
                v_prev = val_map.get((prev, m))
                if v_cur is not None and v_prev not in (None, 0):
                    try:
                        series[m] = (v_cur - v_prev) / v_prev * 100
                    except Exception:
                        continue
            if series:
                yoy_series_by_year[y] = series

        # Calculate latest MoM and YoY
        latest_mom = None
        latest_yoy = None

        if len(ordered) >= 2:
            y, m, v = ordered[-1]
            py, pm, pv = ordered[-2]
            is_consecutive = (py == y and pm == m - 1) or (
                py == y - 1 and pm == 12 and m == 1
            )
            if is_consecutive and pv not in (0, None):
                latest_mom = (v - pv) / pv * 100

            # Find same month last year
            for yy, mm, vv in reversed(ordered[:-1]):
                if yy == y - 1 and mm == m and vv not in (0, None):
                    latest_yoy = (v - vv) / vv * 100
                    break

        return {
            "time_periods": len(ordered),
            "date_range": {
                "start": f"{ordered[0][0]}-{ordered[0][1]:02d}",
                "end": f"{ordered[-1][0]}-{ordered[-1][1]:02d}",
            },
            "values": {f"{y}-{m:02d}": v for (y, m, v) in ordered},
            "latest_mom_change_pct": latest_mom,
            "latest_yoy_change_pct": latest_yoy,
            "mom_series_by_year": mom_series_by_year,
            "yoy_series_by_year": yoy_series_by_year,
            "total_value": sum(v for (y, m, v) in ordered),
            "avg_monthly_value": sum(v for (y, m, v) in ordered) / len(ordered)
            if ordered
            else 0,
        }

    except Exception:
        return None


def _calculate_product_yearly_trends(
    product_df, col: str, year_col: str, aggregation_method: str
) -> Optional[Dict[str, Any]]:
    """Calculate yearly trends for a specific product"""
    try:
        if product_df.height == 0:
            return None

        agg_expr = _get_aggregation_expression(col, aggregation_method)

        # Aggregate by year
        yearly = (
            product_df.select([pl.col(year_col).cast(pl.Int64), pl.col(col)])
            .drop_nulls()
            .group_by(year_col)
            .agg([agg_expr.alias("value")])
            .sort(year_col)
        )

        rows = yearly.to_dicts()
        if len(rows) < 2:
            return None

        # Build ordered list
        ordered = [
            (int(r[year_col]), r["value"]) for r in rows if r.get("value") is not None
        ]

        # Calculate YoY changes
        yoy_series = {}
        for i in range(1, len(ordered)):
            y, v = ordered[i]
            py, pv = ordered[i - 1]
            if pv not in (None, 0):
                try:
                    yoy_series[y] = (v - pv) / pv * 100
                except Exception:
                    continue

        # Latest YoY
        latest_yoy = None
        if len(ordered) >= 2 and ordered[-2][1] not in (None, 0):
            latest_yoy = (ordered[-1][1] - ordered[-2][1]) / ordered[-2][1] * 100

        return {
            "time_periods": len(ordered),
            "date_range": {"start": str(ordered[0][0]), "end": str(ordered[-1][0])},
            "values": {str(y): v for (y, v) in ordered},
            "latest_yoy_change_pct": latest_yoy,
            "yoy_series": yoy_series,
            "total_value": sum(v for (y, v) in ordered),
            "avg_yearly_value": sum(v for (y, v) in ordered) / len(ordered)
            if ordered
            else 0,
        }

    except Exception:
        return None


def _generate_per_product_insights(analysis_result: Dict[str, Any]) -> List[str]:
    """Generate insights for per-product trends analysis"""
    insights = []

    try:
        product_col = analysis_result.get("product_column_used", "productos")
        total_products = analysis_result.get("total_products_analyzed", 0)

        insights.append(f"📊 Análisis de {total_products} {product_col} individuales")

        # Top vs bottom performance gap
        top_details = analysis_result.get("top_3_products", {}).get("details", [])
        bottom_details = analysis_result.get("bottom_3_products", {}).get("details", [])

        if top_details and bottom_details:
            top_value = top_details[0].get("total_value", 0)
            bottom_value = bottom_details[-1].get("total_value", 0)

            if bottom_value > 0:
                gap_ratio = top_value / bottom_value
                insights.append(
                    f"⚖️ Brecha de rendimiento: El mejor producto supera al peor por {gap_ratio:.1f}x"
                )

        # Monthly trends insights
        monthly_trends = analysis_result.get("monthly_trends", {})
        if monthly_trends:
            top_3_trends = monthly_trends.get("top_3", {})
            bottom_3_trends = monthly_trends.get("bottom_3", {})

            # Count products with positive/negative trends
            top_positive_mom = sum(
                1
                for trends in top_3_trends.values()
                if trends.get("latest_mom_change_pct", 0) > 0
            )
            bottom_positive_mom = sum(
                1
                for trends in bottom_3_trends.values()
                if trends.get("latest_mom_change_pct", 0) > 0
            )

            if top_positive_mom > 0:
                insights.append(
                    f"📈 {top_positive_mom}/3 productos top con MoM positivo"
                )
            if bottom_positive_mom > 0:
                insights.append(
                    f"📈 {bottom_positive_mom}/3 productos bottom con MoM positivo"
                )

            # YoY insights
            top_positive_yoy = sum(
                1
                for trends in top_3_trends.values()
                if trends.get("latest_yoy_change_pct", 0) > 0
            )
            bottom_positive_yoy = sum(
                1
                for trends in bottom_3_trends.values()
                if trends.get("latest_yoy_change_pct", 0) > 0
            )

            if top_positive_yoy > 0:
                insights.append(
                    f"📅 {top_positive_yoy}/3 productos top con YoY positivo"
                )
            if bottom_positive_yoy > 0:
                insights.append(
                    f"📅 {bottom_positive_yoy}/3 productos bottom con YoY positivo"
                )

        # Yearly trends insights
        yearly_trends = analysis_result.get("yearly_trends", {})
        if yearly_trends:
            top_3_trends = yearly_trends.get("top_3", {})
            bottom_3_trends = yearly_trends.get("bottom_3", {})

            top_positive_yoy = sum(
                1
                for trends in top_3_trends.values()
                if trends.get("latest_yoy_change_pct", 0) > 0
            )
            bottom_positive_yoy = sum(
                1
                for trends in bottom_3_trends.values()
                if trends.get("latest_yoy_change_pct", 0) > 0
            )

            if top_positive_yoy > 0:
                insights.append(
                    f"📈 {top_positive_yoy}/3 productos top con crecimiento anual"
                )
            if bottom_positive_yoy > 0:
                insights.append(
                    f"📈 {bottom_positive_yoy}/3 productos bottom con crecimiento anual"
                )

        if not insights:
            insights.append("✅ Análisis per-producto completado")

    except Exception:
        insights.append("📊 Análisis individual de productos disponible")

    return insights


def get_analysis_guidance() -> Dict[str, Any]:
    """Provide guidance on when and how to use the core analysis types"""
    return {
        "analysis_types": {
            "overview": {
                "description": "Comprehensive descriptive statistics and data quality assessment",
                "best_for": "Understanding basic data characteristics, distributions, and quality",
                "minimum_requirements": "Any numeric data",
                "recommended_when": "Always - provides foundation for all other analyses",
            },
            "performance": {
                "description": "Rankings, comparisons, outlier detection, and performance gaps",
                "best_for": "Identifying top/bottom performers, competitive analysis, quality control",
                "minimum_requirements": "At least 10 data points",
                "recommended_when": "You have categories/groups to compare or need to find outliers",
            },
            "trends": {
                "description": "Temporal analysis, seasonality detection, and forecasting",
                "best_for": "Understanding time-based patterns, predicting future values",
                "minimum_requirements": "Time column or date data with 5+ periods",
                "recommended_when": "You have time series data and want to understand trends",
            },
            "relationships": {
                "description": "Correlation analysis, regression, and variable dependencies",
                "best_for": "Understanding how variables affect each other, finding drivers",
                "minimum_requirements": "At least 2 numeric columns",
                "recommended_when": "You want to understand variable interactions and dependencies",
            },
        },
        "recommendations": {
            "for_sales_analysts": [
                "🎯 Start with a combination of 'overview', 'trends', 'performance' and 'relationships' for complete insights",
                "📊 Use 'overview' when you first get new data",
                "⚡ Use 'performance' to identify top/bottom performers",
                "📈 Use 'trends' for forecasting and seasonality",
                "🔗 Use 'relationships' to understand what drives metrics",
            ],
            "data_size_guidance": {
                "small_datasets_10_rows": "Focus on 'overview' and 'relationships' analyses",
                "medium_datasets_100_rows": "All four analyses are useful",
                "large_datasets_1000_rows": "All four analyses will provide robust results",
            },
            "common_use_cases": {
                "sales_performance_review": "Use 'performance' + 'trends'",
                "territory_analysis": "Use 'performance' + 'relationships'",
                "product_analysis": "Use 'overview' + 'performance' + 'trends'",
                "forecast_planning": "Use 'trends' analysis specifically",
                "root_cause_analysis": "Use 'relationships' + 'performance'",
            },
        },
    }
