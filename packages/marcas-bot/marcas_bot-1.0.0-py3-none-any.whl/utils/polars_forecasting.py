"""
Forecasting utilities for Polars analytics module
Provides time series forecasting functionality using moving averages and trend extrapolation.
"""

from typing import Dict, List, Any, Optional
from utils.lazy_load import get_polars, get_numpy


def generate_forecasts(
    df,
    col: str,
    slope: float,
    volatility: float,
    forecast_periods: int,
    window_size: int = 3,
    time_column: Optional[str] = None,
    group_by_columns: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Generate forecasts for a time series column using multiple methods.

    If group_by_columns are provided, generates separate forecasts for each group
    and then provides an aggregate forecast as well.

    Args:
        df: Polars DataFrame containing the time series data
        col: Name of the column to forecast
        slope: Trend slope calculated for the column
        volatility: Volatility measure calculated for the column
        forecast_periods: Number of periods to forecast ahead
        window_size: Window size for moving averages
        time_column: Optional time column name
        group_by_columns: Optional list of columns to group by for separate forecasts

    Returns:
        Dictionary with forecasted values and metadata
    """
    if not forecast_periods or forecast_periods < 1:
        return {}

    # If we have grouping columns, generate grouped forecasts
    if group_by_columns and any(gc in df.columns for gc in group_by_columns):
        return _generate_grouped_forecasts(
            df,
            col,
            slope,
            volatility,
            forecast_periods,
            window_size,
            time_column,
            group_by_columns,
        )

    # Standard single-series forecasting
    return _generate_single_forecast(
        df, col, slope, volatility, forecast_periods, window_size, time_column
    )


def _generate_single_forecast(
    df,
    col: str,
    slope: float,
    volatility: float,
    forecast_periods: int,
    window_size: int = 3,
    time_column: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate forecast for a single time series (no grouping).
    """
    # Ensure df is sorted by time column if available
    if time_column and time_column in df.columns:
        df_sorted = df.sort(time_column)
    else:
        df_sorted = df.clone()

    # Extract the values we'll use for forecasting
    values = df_sorted[col].drop_nulls().to_list()

    if len(values) < max(window_size + 1, 3):
        return {}  # Not enough data for forecasting

    # Get the most recent values for forecasting
    recent_values = values[-min(len(values), max(forecast_periods * 3, 10)) :]

    # Determine which forecasting methods to use based on data characteristics
    methods_to_use = []

    # Simple Moving Average - good for stable or noisy series
    if volatility < 0.3:
        methods_to_use.append("sma")

    # Weighted Moving Average - good for recent-weighted forecasts
    if volatility < 0.4:
        methods_to_use.append("wma")

    # Exponential Smoothing - good for trends with some noise
    if abs(slope) > 0.001:
        methods_to_use.append("exp_smoothing")

    # Trend Extrapolation - best for clear trends
    if abs(slope) > 0.005 and volatility < 0.3:
        methods_to_use.append("trend")

    # Default to all methods if none selected
    if not methods_to_use:
        methods_to_use = ["sma", "wma", "exp_smoothing", "trend"]

    # Run all selected forecasting methods
    forecast_results = {}

    for method in methods_to_use:
        if method == "sma":
            forecast_results["sma"] = _forecast_simple_moving_average(
                recent_values, window_size, forecast_periods
            )
        elif method == "wma":
            forecast_results["wma"] = _forecast_weighted_moving_average(
                recent_values, window_size, forecast_periods
            )
        elif method == "exp_smoothing":
            # Determine alpha based on volatility (higher volatility -> lower alpha)
            alpha = max(0.1, min(0.8, 1.0 - volatility))
            forecast_results["exp_smoothing"] = _forecast_exponential_smoothing(
                recent_values, alpha, forecast_periods
            )
        elif method == "trend":
            forecast_results["trend"] = _forecast_trend_extrapolation(
                recent_values, slope, forecast_periods
            )

    # Generate ensemble forecast (average of all methods)
    ensemble_forecast = []
    for i in range(forecast_periods):
        methods_with_forecasts = [
            method for method in forecast_results if i < len(forecast_results[method])
        ]

        if methods_with_forecasts:
            period_values = [
                forecast_results[method][i] for method in methods_with_forecasts
            ]
            ensemble_forecast.append(sum(period_values) / len(period_values))

    forecast_results["ensemble"] = ensemble_forecast

    # Calculate proper 95% confidence intervals based on statistical methodology
    upper_bounds = []
    lower_bounds = []

    # Use 95% confidence interval (1.96 standard deviations for normal distribution)
    confidence_level = 0.95
    z_score = 1.96  # 95% confidence interval

    # Estimate base value for standard error calculation
    base_value = recent_values[-1] if recent_values else 100

    # Calculate percentage changes for better understanding
    period_changes = []
    last_actual = values[-1] if values else base_value

    for i, forecast in enumerate(ensemble_forecast):
        if i == 0:
            change_pct = (
                (forecast - last_actual) / last_actual * 100 if last_actual != 0 else 0
            )
        else:
            change_pct = (
                (forecast - ensemble_forecast[i - 1]) / ensemble_forecast[i - 1] * 100
                if ensemble_forecast[i - 1] != 0
                else 0
            )
        period_changes.append(change_pct)

    # Detect period unit from data structure
    period_unit = _detect_period_unit(df, time_column)

    # Determine trend direction and strength for explanations
    trend_direction = (
        "creciente" if slope > 0 else "decreciente" if slope < 0 else "estable"
    )
    trend_strength = (
        "fuerte" if abs(slope) > 0.02 else "moderado" if abs(slope) > 0.005 else "débil"
    )

    for i, val in enumerate(ensemble_forecast):
        # Standard error increases with forecast horizon (time-based error propagation)
        time_factor = (i + 1) ** 0.5  # Square root of time for error propagation
        standard_error = volatility * base_value * time_factor

        # Calculate margin of error using proper statistical methodology
        margin_of_error = z_score * standard_error
        upper_bound = val + margin_of_error
        lower_bound = max(
            0, val - margin_of_error
        )  # Don't go below 0 for business metrics

        upper_bounds.append(upper_bound)
        lower_bounds.append(lower_bound)

    # Generate enhanced explanations
    forecast_explanation = _generate_forecast_explanation(
        col,
        last_actual,
        ensemble_forecast,
        trend_direction,
        trend_strength,
        volatility,
        forecast_periods,
        period_changes,
        period_unit,
    )

    # Format the final output with proper confidence interval metadata
    return {
        "values": ensemble_forecast,
        "methods_used": methods_to_use,
        "upper_bounds": upper_bounds,
        "lower_bounds": lower_bounds,
        "periods": forecast_periods,
        "details": {method: values for method, values in forecast_results.items()},
        "confidence_intervals": {
            "explanation": "Los límites superior e inferior muestran el rango donde probablemente caerán los valores reales",
            "upper_bounds": upper_bounds,
            "lower_bounds": lower_bounds,
            "confidence_level": f"{confidence_level * 100:.0f}%",
            "statistical_interpretation": f"Hay un {confidence_level * 100:.0f}% de probabilidad de que los valores reales caigan dentro de estos rangos",
            "methodology": "Intervalos calculados usando distribución normal con factor de tiempo para propagación de error",
        },
        "explanation": forecast_explanation,
        "period_changes_pct": period_changes,
    }


def _generate_grouped_forecasts(
    df,
    col: str,
    slope: float,
    volatility: float,
    forecast_periods: int,
    window_size: int,
    time_column: Optional[str],
    group_by_columns: List[str],
) -> Dict[str, Any]:
    """
    Generate separate forecasts for each group (e.g., product, country) and aggregate them.

    This ensures that each product/category gets its own trend analysis and forecast,
    preventing the mixing of different time series that was causing inaccurate results.
    """
    try:
        # Filter valid grouping columns
        valid_groups = [gc for gc in group_by_columns if gc in df.columns]
        if not valid_groups:
            # Fallback to single forecast if no valid groups
            return _generate_single_forecast(
                df, col, slope, volatility, forecast_periods, window_size, time_column
            )

        # Use the first valid grouping column for forecasting
        primary_group = valid_groups[0]

        # Sort by group and time
        sort_columns = [primary_group]
        if time_column and time_column in df.columns:
            sort_columns.append(time_column)
        elif "anio" in df.columns and "mes" in df.columns:
            sort_columns.extend(["anio", "mes"])
        elif "anio" in df.columns:
            sort_columns.append("anio")
        elif "mes" in df.columns:
            sort_columns.append("mes")

        df_sorted = df.sort(sort_columns)

        # Get unique groups
        unique_groups = df_sorted[primary_group].unique().to_list()

        # Generate forecasts for each group
        group_forecasts = {}
        group_metadata = {}
        successful_forecasts = 0
        total_forecast_value = 0

        for group_value in unique_groups:
            # Filter data for this group
            pl = get_polars()
            group_df = df_sorted.filter(pl.col(primary_group) == group_value)

            if group_df.height < 3:  # Need at least 3 data points for forecasting
                continue

            # Calculate group-specific metrics
            group_values = group_df[col].drop_nulls().to_list()
            if len(group_values) < 2:
                continue

            # Calculate group-specific slope and volatility
            if len(group_values) > 1:
                x = list(range(len(group_values)))
                try:
                    group_slope = _calculate_simple_slope(x, group_values)
                except Exception:
                    group_slope = slope  # Fallback to global slope
            else:
                group_slope = slope

            # Calculate group-specific volatility
            if len(group_values) > 1:
                try:
                    np = get_numpy()
                    group_volatility = np.std(
                        [
                            group_values[i] / group_values[i - 1] - 1
                            for i in range(1, len(group_values))
                            if group_values[i - 1] != 0
                        ]
                    )
                except Exception:
                    group_volatility = volatility  # Fallback to global volatility
            else:
                group_volatility = volatility

            # Generate forecast for this group
            try:
                group_forecast = _generate_single_forecast(
                    group_df,
                    col,
                    group_slope,
                    group_volatility,
                    forecast_periods,
                    window_size,
                    time_column,
                )

                if group_forecast and "values" in group_forecast:
                    group_forecasts[str(group_value)] = group_forecast

                    # Store metadata
                    last_actual = group_values[-1] if group_values else 0
                    group_metadata[str(group_value)] = {
                        "last_actual_value": last_actual,
                        "data_points": len(group_values),
                        "group_slope": group_slope,
                        "group_volatility": group_volatility,
                        "forecast_sum": sum(group_forecast["values"]),
                    }

                    successful_forecasts += 1
                    total_forecast_value += sum(group_forecast["values"])

            except Exception as e:
                # Skip groups that fail forecasting
                continue

        # Generate aggregate forecast by summing individual group forecasts
        aggregate_forecast = [0] * forecast_periods
        aggregate_upper_bounds = [0] * forecast_periods
        aggregate_lower_bounds = [0] * forecast_periods

        if group_forecasts:
            for period_idx in range(forecast_periods):
                period_sum = 0
                period_upper_sum = 0
                period_lower_sum = 0

                for group_name, forecast_data in group_forecasts.items():
                    if period_idx < len(forecast_data.get("values", [])):
                        period_sum += forecast_data["values"][period_idx]

                        if "upper_bounds" in forecast_data and period_idx < len(
                            forecast_data["upper_bounds"]
                        ):
                            period_upper_sum += forecast_data["upper_bounds"][
                                period_idx
                            ]
                        else:
                            period_upper_sum += (
                                forecast_data["values"][period_idx] * 1.2
                            )  # 20% buffer

                        if "lower_bounds" in forecast_data and period_idx < len(
                            forecast_data["lower_bounds"]
                        ):
                            period_lower_sum += forecast_data["lower_bounds"][
                                period_idx
                            ]
                        else:
                            period_lower_sum += max(
                                0, forecast_data["values"][period_idx] * 0.8
                            )  # 80% lower bound

                aggregate_forecast[period_idx] = period_sum
                aggregate_upper_bounds[period_idx] = period_upper_sum
                aggregate_lower_bounds[period_idx] = period_lower_sum

        # Calculate aggregate metrics
        total_current_value = sum(
            group_meta["last_actual_value"] for group_meta in group_metadata.values()
        )

        # Calculate period changes for aggregate
        period_changes = []
        for i, forecast_val in enumerate(aggregate_forecast):
            if i == 0:
                change_pct = (
                    (forecast_val - total_current_value) / total_current_value * 100
                    if total_current_value != 0
                    else 0
                )
            else:
                change_pct = (
                    (forecast_val - aggregate_forecast[i - 1])
                    / aggregate_forecast[i - 1]
                    * 100
                    if aggregate_forecast[i - 1] != 0
                    else 0
                )
            period_changes.append(change_pct)

        # Determine aggregate trend
        if aggregate_forecast:
            total_change = aggregate_forecast[-1] - total_current_value
            total_change_pct = (
                (total_change / total_current_value * 100)
                if total_current_value != 0
                else 0
            )
            trend_direction = (
                "creciente"
                if total_change_pct > 5
                else "decreciente"
                if total_change_pct < -5
                else "estable"
            )
            trend_strength = (
                "fuerte"
                if abs(total_change_pct) > 20
                else "moderado"
                if abs(total_change_pct) > 10
                else "débil"
            )
        else:
            trend_direction = "estable"
            trend_strength = "débil"
            total_change_pct = 0

        # Detect period unit
        period_unit = _detect_period_unit(df, time_column)

        # Generate explanation for grouped forecast
        grouped_explanation = {
            "resumen_ejecutivo": f"📈 PRONÓSTICO AGRUPADO POR {primary_group.upper()}: Se analizaron {successful_forecasts} {primary_group}s individualmente. El pronóstico agregado muestra una tendencia {trend_direction} {trend_strength} con un cambio total proyectado del {total_change_pct:+.1f}% en {forecast_periods} {period_unit}s.",
            "metodologia": f"🔬 METODOLOGÍA AGRUPADA: Se generaron pronósticos individuales para cada {primary_group} usando sus propias tendencias históricas, evitando la mezcla de series temporales diferentes. Los pronósticos individuales se agregaron para obtener el pronóstico total. Esto garantiza mayor precisión al respetar los patrones únicos de cada {primary_group}.",
            "interpretacion_grupos": f"📊 ANÁLISIS POR GRUPOS: De {len(unique_groups)} {primary_group}s únicos, {successful_forecasts} tienen suficientes datos para pronósticos confiables. Los {primary_group}s con mejor desempeño histórico contribuyen proporcionalmente más al pronóstico agregado.",
            "factores_clave": f"🔑 FACTORES GRUPALES: Cada {primary_group} mantiene su propia tendencia y volatilidad. Los {primary_group}s con tendencias crecientes compensan aquellos con tendencias decrecientes en el agregado. La diversificación entre {primary_group}s reduce el riesgo total del pronóstico.",
            "recomendaciones_uso": f"💡 RECOMENDACIONES: Monitoree tanto el pronóstico agregado como los pronósticos individuales por {primary_group}. Identifique {primary_group}s con alto potencial de crecimiento para estrategias focalizadas. Use los pronósticos individuales para planificación detallada por {primary_group}.",
        }

        # Return comprehensive grouped forecast result
        return {
            "values": aggregate_forecast,
            "upper_bounds": aggregate_upper_bounds,
            "lower_bounds": aggregate_lower_bounds,
            "periods": forecast_periods,
            "methods_used": ["grouped_ensemble"],
            "grouped_by": primary_group,
            "groups_analyzed": len(unique_groups),
            "successful_forecasts": successful_forecasts,
            "group_forecasts": group_forecasts,
            "group_metadata": group_metadata,
            "aggregate_metadata": {
                "total_current_value": total_current_value,
                "total_forecast_value": sum(aggregate_forecast),
                "trend_direction": trend_direction,
                "trend_strength": trend_strength,
            },
            "explanation": grouped_explanation,
            "period_changes_pct": period_changes,
            "confidence_intervals": {
                "explanation": f"Los intervalos de confianza se calcularon agregando los límites individuales de cada {primary_group}",
                "upper_bounds": aggregate_upper_bounds,
                "lower_bounds": aggregate_lower_bounds,
                "confidence_level": "95%",
                "methodology": f"Agregación de intervalos individuales por {primary_group} con ajuste por diversificación",
            },
        }

    except Exception as e:
        # Fallback to single forecast if grouped forecasting fails
        return _generate_single_forecast(
            df, col, slope, volatility, forecast_periods, window_size, time_column
        )


def _calculate_simple_slope(x: List[int], y: List[float]) -> float:
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


def _forecast_simple_moving_average(
    values: List[float], window_size: int, forecast_periods: int
) -> List[float]:
    """Generate forecast using Simple Moving Average"""
    if len(values) < window_size:
        window_size = len(values)

    # Start with the last moving average
    last_ma = sum(values[-window_size:]) / window_size
    forecasts = [last_ma]

    # For remaining periods, shift the window forward by including
    # the previous forecast
    rolling_window = values[-(window_size - 1) :] + forecasts

    for _ in range(1, forecast_periods):
        next_ma = sum(rolling_window[-window_size:]) / window_size
        forecasts.append(next_ma)
        rolling_window.append(next_ma)

    return forecasts


def _forecast_weighted_moving_average(
    values: List[float], window_size: int, forecast_periods: int
) -> List[float]:
    """Generate forecast using Weighted Moving Average with linear weights"""
    if len(values) < window_size:
        window_size = len(values)

    # Create linearly increasing weights (more recent = higher weight)
    weights = list(range(1, window_size + 1))
    weight_sum = sum(weights)

    # Initial forecast
    initial_window = values[-window_size:]
    weighted_sum = sum(w * v for w, v in zip(weights, initial_window))
    forecasts = [weighted_sum / weight_sum]

    # For remaining periods, shift the window forward
    rolling_window = values[-(window_size - 1) :] + forecasts

    for _ in range(1, forecast_periods):
        window = rolling_window[-window_size:]
        weighted_sum = sum(w * v for w, v in zip(weights, window))
        next_forecast = weighted_sum / weight_sum
        forecasts.append(next_forecast)
        rolling_window.append(next_forecast)

    return forecasts


def _forecast_exponential_smoothing(
    values: List[float], alpha: float, forecast_periods: int
) -> List[float]:
    """Generate forecast using Exponential Smoothing"""
    if not values:
        return []

    # Simple exponential smoothing formula: forecast = alpha * actual + (1 - alpha) * previous_forecast
    last_actual = values[-1]
    forecasts = [last_actual]  # Start with last actual value

    for _ in range(1, forecast_periods):
        next_forecast = alpha * values[-1] + (1 - alpha) * forecasts[-1]
        forecasts.append(next_forecast)

    return forecasts


def _forecast_trend_extrapolation(
    values: List[float], slope: float, forecast_periods: int
) -> List[float]:
    """Generate forecast using trend extrapolation"""
    if not values:
        return []

    # Use the provided slope or calculate it if not provided
    if slope == 0:
        # Simple linear regression to calculate slope
        x = list(range(len(values)))
        mean_x = sum(x) / len(x)
        mean_y = sum(values) / len(values)

        numerator = sum(
            (x[i] - mean_x) * (values[i] - mean_y) for i in range(len(values))
        )
        denominator = sum((x[i] - mean_x) ** 2 for i in range(len(values)))

        slope = numerator / denominator if denominator != 0 else 0

    # Calculate intercept using the last point and slope
    last_x = len(values) - 1
    last_y = values[-1]
    intercept = last_y - (slope * last_x)

    # Generate forecasts using the trend line equation: y = mx + b
    forecasts = []
    for i in range(1, forecast_periods + 1):
        next_x = last_x + i
        next_y = (slope * next_x) + intercept
        forecasts.append(next_y)

    return forecasts


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


def _generate_forecast_explanation(
    column: str,
    last_value: float,
    forecasts: List[float],
    trend_direction: str,
    trend_strength: str,
    volatility: float,
    periods: int,
    period_changes: List[float],
    period_unit: str = "período",
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
            period_unit,
        ),
        "metodologia": _generate_methodology_explanation(
            trend_direction, trend_strength, volatility
        ),
        "interpretacion_valores": _generate_value_interpretation(
            forecasts, last_value, period_changes, period_unit=period_unit
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
    period_unit: str = "período",
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

    period_text = f"{periods} {period_unit}s" if periods > 1 else f"1 {period_unit}"

    return f"📈 PRONÓSTICO PARA {column.upper()}: Basado en las tendencias actuales, se espera que {column} {direction_text} {change_magnitude} en los próximos {period_text}. El valor actual de {current_value:,.2f} podría llegar a {final_forecast:,.2f} (cambio del {total_change_pct:+.1f}%)."


def _generate_methodology_explanation(
    trend_direction: str, trend_strength: str, volatility: float
) -> str:
    """Explain the forecasting methodology"""

    volatility_desc = (
        "alta" if volatility > 0.3 else "moderada" if volatility > 0.15 else "baja"
    )

    return f"🔬 METODOLOGÍA: Este pronóstico utiliza un ensemble de múltiples métodos (promedio móvil, ponderado, suavizado exponencial, extrapolación de tendencia) basado en el patrón {trend_direction} {trend_strength} observado en los datos históricos. La volatilidad {volatility_desc} ({volatility:.1%}) se incorpora para crear intervalos de confianza del 95%. El modelo ajusta la confianza hacia períodos futuros más lejanos."


def _generate_value_interpretation(
    forecasts: List[float],
    last_value: float,
    period_changes: List[float],
    upper_bounds: List[float] = None,
    lower_bounds: List[float] = None,
    confidence_level: str = "95%",
    period_unit: str = "período",
) -> str:
    """Explain what the forecasted values mean including confidence intervals"""

    if not forecasts:
        return "No se pudieron generar pronósticos."

    next_period = forecasts[0]
    next_change = period_changes[0] if period_changes else 0

    avg_change = sum(period_changes) / len(period_changes) if period_changes else 0

    interpretation = f"📋 INTERPRETACIÓN DE VALORES:\n"

    # Define what "período" means in this context
    interpretation += f"📅 DEFINICIÓN DE PERÍODO: Un '{period_unit}' representa la unidad de tiempo detectada en sus datos. "
    interpretation += f"Los pronósticos muestran valores esperados para cada {period_unit} futuro consecutivo.\n\n"

    interpretation += f"• Próximo {period_unit}: {next_period:,.2f} ({next_change:+.1f}% vs. actual)\n"

    # Add confidence interval for next period if available
    if (
        upper_bounds
        and lower_bounds
        and len(upper_bounds) > 0
        and len(lower_bounds) > 0
    ):
        next_upper = upper_bounds[0]
        next_lower = lower_bounds[0]
        interpretation += f"  └─ Rango probable: {next_lower:,.2f} - {next_upper:,.2f} ({confidence_level} confianza)\n"
        interpretation += f"  └─ Esto significa que el valor real del próximo {period_unit} tiene una alta probabilidad de caer dentro de este rango\n"

    interpretation += f"• Cambio promedio por {period_unit}: {avg_change:+.1f}%\n"
    interpretation += f"• Valor final proyectado ({period_unit} {len(forecasts)}): {forecasts[-1]:,.2f}\n"

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
        interpretation += f"• Rango de valores centrales (todos los {period_unit}s): {min_value:,.2f} - {max_value:,.2f}"

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
        factors += f"• 📋 Tendencia estable sugiere valores similares\n"

    # Volatility factor
    if volatility > 0.3:
        factors += f"• ⚡ Alta volatilidad ({volatility:.1%}) aumenta incertidumbre\n"
        factors += f"• 📈 Pueden ocurrir cambios bruscos inesperados"
    elif volatility > 0.15:
        factors += f"• 🎯 Volatilidad moderada ({volatility:.1%}) permite predicciones razonables\n"
        factors += f"• 📋 Cambios graduales son más probables"
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

    recommendations += "• 📋 Monitoree los valores reales vs. pronósticos\n"
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
