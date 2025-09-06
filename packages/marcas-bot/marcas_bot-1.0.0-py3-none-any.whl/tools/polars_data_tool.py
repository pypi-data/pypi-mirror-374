"""
Polars Data Analysis Tool

A structured tool that provides advanced data manipulation and statistical analysis
capabilities using Polars. This tool can be used by sales agents to perform
sophisticated analytics on tabular data.
"""

from typing import Dict, List, Any, Optional
import json
from langchain_core.tools import Tool, StructuredTool
from schemas.polars_analysis_input import PolarsAnalysisInput
from utils.polars_analytics import parse_tabular_data, analyze_data, AnalysisType
from utils.logger import logger
from utils.data_registry import get_data as registry_get_data


def polars_data_analysis_tool(
    raw_data: str = "",
    analysis_type: str = "overview",
    data_ref: Optional[str] = None,
    target_columns: Optional[str] = None,
    group_by_columns: Optional[str] = None,
    time_column: Optional[str] = None,
    aggregation_method: str = "sum",
    percentiles: str = "0.25,0.5,0.75",
    window_size: int = 3,
    correlation_threshold: float = 0.3,
    outlier_method: str = "iqr",
    outlier_threshold: float = 1.5,
    trend_periods: int = 5,
    statistical_tests: bool = False,
    confidence_level: float = 0.95,
    top_n: int = 10,
) -> str:
    """
    High-performance data analysis with Polars (only four supported types).

    Supported analysis_type values:
    - "overview": Summary (descriptive + distributions + data quality)
    - "performance": Rankings, group comparisons, outliers, performance gaps
    - "trends": Temporal trends, seasonality, forecasting
    - "relationships": Correlations, regressions, dependencies

    Args:
        raw_data (str): Tabular data in markdown, CSV, or JSON format
        analysis_type (str): One of "overview", "performance", "trends", "relationships"
        target_columns (str, optional): Comma-separated list of columns to analyze
        group_by_columns (str, optional): Comma-separated list of columns to group by
        time_column (str, optional): Column name to use for temporal analysis
        aggregation_method (str): Aggregation method ("sum", "mean", "median", "count", "min", "max", "std", "var")
        percentiles (str): Comma-separated percentiles to calculate (e.g., "0.1,0.25,0.5,0.75,0.9")
        window_size (int): Window size for moving averages and rolling calculations
        correlation_threshold (float): Minimum correlation strength to report (0.0-1.0)
        outlier_method (str): Method for outlier detection ("iqr" or "zscore")
        outlier_threshold (float): Threshold for outlier detection (1.5 for IQR, 2-3 for zscore)
        trend_periods (int): Number of recent periods to analyze for trends
        statistical_tests (bool): Whether to perform statistical significance tests
        confidence_level (float): Confidence level for statistical tests (0.90, 0.95, 0.99)
        top_n (int): Number of top/bottom items to show in rankings

    Returns:
        str: Formatted analysis results with insights and recommendations

    Examples:
        # Overview summary
        polars_data_analysis_tool(table_data, analysis_type="overview", target_columns="ventas,unidades")

        # Trends with forecasting
        polars_data_analysis_tool(table_data, analysis_type="trends", time_column="mes", target_columns="ventas")
    """

    # Build parameter description for logging
    params = [f"analysis_type='{analysis_type}'"]
    if target_columns:
        params.append(f"target_columns='{target_columns}'")
    if group_by_columns:
        params.append(f"group_by_columns='{group_by_columns}'")
    if time_column:
        params.append(f"time_column='{time_column}'")
    params.append(f"data_length={len(raw_data) if raw_data else 0}")

    params_description = ", ".join(params)
    logger.info(f"Starting Polars analysis: {params_description}")

    # Log data preview for debugging
    # Resolve effective raw text: prefer data_ref if provided
    effective_raw = None
    if data_ref:
        ref_data = registry_get_data(data_ref)
        if ref_data:
            effective_raw = ref_data
            logger.debug(f"Using data_ref='{data_ref}' with length {len(ref_data)}")
        else:
            logger.warning(
                f"data_ref key '{data_ref}' not found; falling back to raw_data"
            )
    if effective_raw is None:
        if raw_data:
            effective_raw = raw_data
            data_preview = (
                effective_raw[:200].replace("\n", " ") + "..."
                if len(effective_raw) > 200
                else effective_raw.replace("\n", " ")
            )
            logger.debug(f"Raw data preview: '{data_preview}'")
        else:
            logger.warning("No raw data provided to Polars tool and no data_ref")
            return "❌ No se proporcionaron datos para analizar"

    try:
        logger.debug("Attempting to parse tabular data with Polars...")
        # Pre-sanitize raw data (extract JSON array if present, strip code fences, handle DATA_JSON prefix)
        sanitized = _extract_json_array(effective_raw)
        df = None
        if sanitized:
            # Try direct JSON load for array-of-objects
            try:
                import json as _json

                loaded = _json.loads(sanitized)
                if isinstance(loaded, list) and loaded and isinstance(loaded[0], dict):
                    from utils.lazy_load import get_polars

                    pl = get_polars()
                    df = pl.DataFrame(loaded)
                    logger.debug(
                        f"Loaded DataFrame from JSON array: {df.shape[0]} rows × {df.shape[1]} columns"
                    )
                else:
                    logger.debug(
                        "Sanitized JSON not a list of dicts; will fallback to general parser"
                    )
            except Exception as e:
                logger.debug(
                    f"Direct JSON load failed: {e}; will fallback to general parser"
                )
        if df is None:
            # General parser supports markdown/CSV/JSON (object stream)
            df = parse_tabular_data(raw_data if not sanitized else sanitized)

        if df is None:
            logger.warning(f"Failed to parse tabular data - {params_description}")
            return """❌ **ERROR EN DATOS**

No se pudo parsear los datos proporcionados.

**Formatos soportados:**
- Tablas Markdown con separadores |
- Datos CSV con headers
- Objetos JSON

**Ejemplo de formato esperado:**
```
| Producto | Ventas | Region |
|----------|--------|--------|
| Leche    | 1000   | Norte  |
| Yogurt   | 800    | Sur    |
```

Por favor, proporciona los datos en uno de estos formatos."""

        # Log successful data parsing
        df_shape = df.shape if hasattr(df, "shape") else ("unknown", "unknown")
        df_columns = list(df.columns) if hasattr(df, "columns") else []
        logger.debug(
            f"Data parsed successfully: {df_shape[0]} rows × {df_shape[1]} columns"
        )
        logger.debug(f"Column names: {df_columns}")

        # Parse string parameters
        target_cols = (
            [col.strip() for col in target_columns.split(",")]
            if target_columns
            else None
        )
        group_cols = (
            [col.strip() for col in group_by_columns.split(",")]
            if group_by_columns
            else None
        )
        percentile_list = [
            float(p.strip()) for p in percentiles.split(",") if p.strip()
        ]

        # Validate analysis type
        valid_types = [e.value for e in AnalysisType]
        if analysis_type not in valid_types:
            logger.warning(
                f"Invalid analysis type '{analysis_type}' - {params_description}"
            )
            return f"""❌ **TIPO DE ANÁLISIS INVÁLIDO**

El tipo de análisis '{analysis_type}' no es válido.

**Tipos disponibles:**
- `overview`: Resumen general (descriptivo + distribución + calidad de datos)
- `performance`: Rendimiento (rankings, comparativos, outliers, brechas)
- `trends`: Tendencias (temporal, estacionalidad, pronósticos)
- `relationships`: Relaciones (correlaciones, regresión, dependencias)

**Ejemplo:** `analysis_type="trends"`"""

        # Log analysis parameters before execution
        analysis_params = [f"target_cols={target_cols}", f"group_cols={group_cols}"]
        logger.debug(
            f"Starting analyze_data with parameters: {', '.join(analysis_params)}"
        )

        # Perform analysis
        results = analyze_data(
            df=df,
            analysis_type=analysis_type,
            target_columns=target_cols,
            group_by_columns=group_cols,
            time_column=time_column,
            aggregation_method=aggregation_method,
            percentiles=percentile_list,
            window_size=window_size,
            correlation_threshold=correlation_threshold,
            outlier_method=outlier_method,
            outlier_threshold=outlier_threshold,
            trend_periods=trend_periods,
            statistical_tests=statistical_tests,
            confidence_level=confidence_level,
            top_n=top_n,
        )

        # Log analysis completion with detailed results
        logger.debug(f"analyze_data completed, result keys: {list(results.keys())}")

        # Log complete analysis results for debugging and auditing
        _log_complete_analysis_results(results, analysis_type, params_description)

        # Check for analysis errors
        if "error" in results:
            logger.error(f"Analysis error: {results['error']} - {params_description}")
            return f"""❌ **ERROR EN ANÁLISIS**

{results["error"]}

**Sugerencias:**
- Verifica que las columnas especificadas existan en los datos
- Asegúrate de que hay suficientes datos para el tipo de análisis
- Revisa los parámetros de configuración"""

        # Log successful completion with summary
        data_info = results.get("data_info", {})
        shape = data_info.get("shape", {})
        analysis_summary = results.get("analysis", {})
        insights_count = len(results.get("insights", []))
        recommendations_count = len(results.get("recommendations", []))

        result_summary = [f"dataset: {shape.get('rows', 0)}×{shape.get('columns', 0)}"]
        if insights_count > 0:
            result_summary.append(f"{insights_count} insights")
        if recommendations_count > 0:
            result_summary.append(f"{recommendations_count} recommendations")
        if analysis_summary:
            result_summary.append(f"{len(analysis_summary)} analysis sections")

        logger.info(
            f"Polars analysis completed: {', '.join(result_summary)} - {params_description}"
        )

        # Format results
        formatted_result = _format_analysis_results(results, analysis_type)
        logger.debug(f"Formatted result length: {len(formatted_result)} characters")

        # Log the complete formatted output that the sales agent actually sees
        logger.info(f"=== COMPLETE FORMATTED OUTPUT ({analysis_type}) ===")
        logger.info(formatted_result)
        logger.info("=== END FORMATTED OUTPUT ===")

        return formatted_result

    except Exception as e:
        logger.error(f"Polars analysis failed: {str(e)} - {params_description}")
        return f"""❌ **ERROR INESPERADO**

Se produjo un error durante el análisis: {str(e)}

**Soluciones sugeridas:**
1. Verifica el formato de los datos de entrada
2. Revisa los parámetros de configuración
3. Asegúrate de que los nombres de columnas sean correctos
4. Intenta con un análisis más simple primero

**Para soporte, incluye:**
- Tipo de análisis solicitado
- Estructura de los datos
- Parámetros utilizados"""


def _extract_json_array(text: str) -> Optional[str]:
    """Extract a JSON array substring from mixed text.
    Handles prefixes like 'DATA_JSON:' and code fences, and double-encoded JSON strings.
    Returns the array string (e.g., '[{...}, {...}]') or None if not found.
    """
    if not text:
        return None
    s = text.strip()
    # If enclosed in code fences, strip them
    if s.startswith("```") and s.endswith("```"):
        s = s.strip("`").strip()
        # If there's a language tag like ```json
        if "\n" in s:
            s = s.split("\n", 1)[1].strip()
    # If prefixed with DATA_JSON:
    if s.upper().startswith("DATA_JSON"):
        # split on first '[' after prefix
        idx = s.find("[")
        if idx != -1:
            s = s[idx:]
    # If string starts with a quoted array, e.g., "[ {...} ]"
    if (s.startswith('"[') and s.endswith(']"')) or (
        s.startswith("'[") and s.endswith("]'")
    ):
        try:
            import json as _json

            s = _json.loads(s)
        except Exception:
            return None
    # Extract the outermost [ ... ]
    lb = s.find("[")
    rb = s.rfind("]")
    if lb != -1 and rb != -1 and rb > lb:
        candidate = s[lb : rb + 1].strip()
        # quick sanity check
        if candidate.startswith("[") and candidate.endswith("]"):
            return candidate
    return None


def _log_complete_analysis_results(
    results: Dict[str, Any], analysis_type: str, params_description: str
) -> None:
    """Log comprehensive analysis results for debugging and auditing"""
    import json

    try:
        # Create a sanitized version of results for logging (avoid potential serialization issues)
        sanitized_results = _sanitize_results_for_logging(results)

        # Log analysis overview
        data_info = results.get("data_info", {})
        shape = data_info.get("shape", {})
        logger.info(
            f"=== COMPLETE ANALYSIS RESULTS === \n"
            f"Analysis Type: {analysis_type} | Parameters: {params_description} \n"
            f"Dataset: {shape.get('rows', 0)} rows × {shape.get('columns', 0)} columns \n"
            f"Timestamp: {results.get('timestamp', 'N/A')}"
        )

        # Log analysis parameters
        parameters = results.get("parameters", {})
        if parameters:
            logger.info(
                f"Analysis Parameters: {json.dumps(parameters, indent=2, ensure_ascii=False)}"
            )

        # Log data information
        if data_info:
            logger.info(
                f"Data Information: {json.dumps(data_info, indent=2, ensure_ascii=False)}"
            )

        # Log main analysis results by section
        analysis = results.get("analysis", {})
        if analysis:
            logger.info(f"Analysis Results Structure: {list(analysis.keys())}")

            # Log each analysis section with size information
            for section_name, section_data in analysis.items():
                if isinstance(section_data, dict):
                    section_keys = list(section_data.keys())
                    logger.info(
                        f"  • {section_name}: {len(section_keys)} items - {section_keys[:10]}{'...' if len(section_keys) > 10 else ''}"
                    )

                    # Log detailed content for key sections
                    if section_name in [
                        "summary",
                        "performance_summary",
                        "trend_summary",
                        "relationship_summary",
                    ]:
                        logger.debug(
                            f"    {section_name} Content: {json.dumps(section_data, indent=4, ensure_ascii=False, default=str)}"
                        )
                elif isinstance(section_data, list):
                    logger.info(f"  • {section_name}: {len(section_data)} items")
                    if (
                        section_data and len(section_data) <= 10
                    ):  # Log small lists completely
                        logger.debug(
                            f"    {section_name} Content: {json.dumps(section_data, indent=4, ensure_ascii=False, default=str)}"
                        )
                else:
                    logger.info(f"  • {section_name}: {type(section_data).__name__}")

        # Log insights
        insights = results.get("insights", [])
        if insights:
            logger.info(f"Generated Insights ({len(insights)}):")
            for i, insight in enumerate(insights, 1):
                logger.info(f"  {i}. {insight}")

        # Log recommendations
        recommendations = results.get("recommendations", [])
        if recommendations:
            logger.info(f"Generated Recommendations ({len(recommendations)}):")
            for i, rec in enumerate(recommendations, 1):
                logger.info(f"  {i}. {rec}")

        # Log performance metrics if available
        if analysis_type == "performance":
            _log_performance_analysis_details(analysis)
        elif analysis_type == "trends":
            _log_trends_analysis_details(analysis)
        elif analysis_type == "overview":
            _log_overview_analysis_details(analysis)
        elif analysis_type == "relationships":
            _log_relationships_analysis_details(analysis)

        logger.info("=== END COMPLETE ANALYSIS RESULTS ===")

    except Exception as e:
        logger.error(f"Failed to log complete analysis results: {str(e)}")


def _sanitize_results_for_logging(results: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize results to avoid JSON serialization issues while preserving structure"""
    import numpy as np

    def sanitize_value(value):
        if isinstance(value, dict):
            return {k: sanitize_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [sanitize_value(v) for v in value]
        elif isinstance(value, (np.integer, np.floating)):
            return float(value) if not np.isnan(value) else None
        elif isinstance(value, np.ndarray):
            return value.tolist()
        elif hasattr(value, "__dict__"):
            return str(value)
        else:
            return value

    return sanitize_value(results)


def _log_performance_analysis_details(analysis: Dict[str, Any]) -> None:
    """Log detailed performance analysis results"""
    logger.info("--- PERFORMANCE ANALYSIS DETAILS ---")

    # Log rankings
    rankings = analysis.get("rankings", {})
    if rankings:
        logger.info(f"Rankings Analysis: {len(rankings)} columns analyzed")
        for col, ranking_data in list(rankings.items())[:3]:  # Top 3 columns
            if isinstance(ranking_data, dict):
                top_performers = ranking_data.get("top_performers", [])
                logger.info(f"  • {col}: Top {len(top_performers)} performers")
                if top_performers:
                    logger.debug(
                        f"    Top 3 values: {[p.get(col, 0) for p in top_performers[:3]]}"
                    )

    # Log comparisons
    comparisons = analysis.get("comparisons", {})
    if comparisons:
        logger.info(f"Comparative Analysis: {len(comparisons)} group comparisons")
        for comp_name, comp_data in list(comparisons.items())[:3]:
            if isinstance(comp_data, dict):
                groups = comp_data.get("groups", [])
                gap = comp_data.get("performance_gap_pct", 0)
                logger.info(
                    f"  • {comp_name}: {len(groups)} groups, {gap:.1f}% performance gap"
                )

    # Log outliers
    outliers = analysis.get("outliers", {})
    if outliers:
        total_outliers = sum(
            col_data.get("outliers_count", 0)
            for col_data in outliers.values()
            if isinstance(col_data, dict)
        )
        logger.info(
            f"Outlier Analysis: {total_outliers} outliers detected across {len(outliers)} columns"
        )


def _log_trends_analysis_details(analysis: Dict[str, Any]) -> None:
    """Log detailed trends analysis results"""
    logger.info("--- TRENDS ANALYSIS DETAILS ---")

    # Log trend summary
    trend_summary = analysis.get("trend_summary", {})
    if trend_summary:
        growing = len(trend_summary.get("growing_metrics", []))
        declining = len(trend_summary.get("declining_metrics", []))
        stable = len(trend_summary.get("stable_metrics", []))
        logger.info(
            f"Trend Summary: {growing} growing, {declining} declining, {stable} stable metrics"
        )

    # Log forecast information
    forecasts = analysis.get("forecasts", {})
    forecast_indicators = analysis.get("forecast_indicators", {})
    if forecasts and forecast_indicators:
        high_confidence = sum(
            1
            for indicators in forecast_indicators.values()
            if indicators.get("forecast_confidence") == "alta"
        )
        logger.info(
            f"Forecasting: {len(forecasts)} metrics forecasted, {high_confidence} with high confidence"
        )

    # Log temporal analysis details
    temporal_analysis = analysis.get("temporal_analysis", {})
    if temporal_analysis:
        logger.info(f"Temporal Analysis: {len(temporal_analysis)} columns analyzed")
        for col, trend_info in list(temporal_analysis.items())[:2]:
            if isinstance(trend_info, dict):
                direction = trend_info.get("trend_direction", "N/A")
                volatility = trend_info.get("volatility_level", "N/A")
                logger.info(f"  • {col}: {direction} trend, {volatility} volatility")


def _log_overview_analysis_details(analysis: Dict[str, Any]) -> None:
    """Log detailed overview analysis results"""
    logger.info("--- OVERVIEW ANALYSIS DETAILS ---")

    # Log descriptive statistics
    desc_stats = analysis.get("descriptive_stats", {})
    if desc_stats:
        logger.info(f"Descriptive Statistics: {len(desc_stats)} columns analyzed")
        for col, stats in list(desc_stats.items())[:3]:
            if isinstance(stats, dict) and "mean" in stats:
                mean = stats.get("mean", 0)
                std = stats.get("std", 0)
                cv = stats.get("coefficient_of_variation", 0)
                logger.info(f"  • {col}: mean={mean:.2f}, std={std:.2f}, cv={cv:.3f}")

    # Log data quality information
    data_quality = analysis.get("data_quality", {})
    if data_quality:
        issues_found = data_quality.get("issues_found", 0)
        logger.info(f"Data Quality: {issues_found} issues found")

    # Log statistical insights
    statistical_insights = analysis.get("statistical_insights", [])
    if statistical_insights:
        logger.info(
            f"Statistical Insights: {len(statistical_insights)} insights generated"
        )


def _log_relationships_analysis_details(analysis: Dict[str, Any]) -> None:
    """Log detailed relationships analysis results"""
    logger.info("--- RELATIONSHIPS ANALYSIS DETAILS ---")

    # Log relationship summary
    rel_summary = analysis.get("relationship_summary", {})
    if rel_summary:
        total_corr = rel_summary.get("total_correlations_found", 0)
        significant = rel_summary.get("significant_relationships", 0)
        strong = rel_summary.get("strong_relationships", 0)
        logger.info(
            f"Relationship Summary: {total_corr} correlations, {significant} significant, {strong} strong"
        )

    # Log correlations
    correlations = analysis.get("correlations", {})
    if correlations:
        significant_corrs = correlations.get("significant_correlations", [])
        logger.info(
            f"Correlations: {len(significant_corrs)} significant correlations found"
        )

    # Log regressions
    regressions = analysis.get("regressions", {})
    if regressions:
        logger.info(f"Regressions: {len(regressions)} regression analyses performed")


def _format_analysis_results(results: Dict[str, Any], analysis_type: str) -> str:
    """Format analysis results into a readable report"""

    # Extract key components
    data_info = results.get("data_info", {})
    analysis = results.get("analysis", {})
    insights = results.get("insights", [])
    recommendations = results.get("recommendations", [])
    parameters = results.get("parameters", {})

    # Build formatted response
    response_parts = []

    # Header with analysis type and data info
    shape = data_info.get("shape", {})
    response_parts.append(f"# 📊 ANÁLISIS DE DATOS AVANZADO")
    response_parts.append(
        f"**Tipo:** {analysis_type.title()} | **Dataset:** {shape.get('rows', 0)} filas × {shape.get('columns', 0)} columnas"
    )

    # Include grouping information in header
    group_cols = parameters.get("group_by_columns") or []
    if isinstance(group_cols, list) and group_cols:
        response_parts.append(f"**Agrupación:** {', '.join(group_cols)}")
    elif isinstance(group_cols, str) and group_cols.strip():
        response_parts.append(f"**Agrupación:** {group_cols}")
    else:
        response_parts.append("**Agrupación:** ninguna")

    # Analysis-specific results - Handle both new simplified types and legacy types
    if analysis_type == "overview":
        response_parts.append("\n## 🔍 RESUMEN GENERAL")
        response_parts.extend(_format_overview_results(analysis))

    elif analysis_type == "performance":
        response_parts.append("\n## 🏆 ANÁLISIS DE RENDIMIENTO")
        response_parts.extend(_format_performance_results(analysis))

    elif analysis_type == "trends":
        response_parts.append("\n## 📈 ANÁLISIS DE TENDENCIAS")
        response_parts.extend(_format_trends_results(analysis))

    elif analysis_type == "relationships":
        response_parts.append("\n## 🔗 ANÁLISIS DE RELACIONES")
        response_parts.extend(_format_relationships_results(analysis))

    # Legacy detailed analysis types (backward compatibility)

    # Insights section
    if insights:
        response_parts.append("\n## 💡 INSIGHTS CLAVE")
        for insight in insights:
            response_parts.append(f"• {insight}")

    # Recommendations section
    if recommendations:
        response_parts.append("\n## 🎯 RECOMENDACIONES")
        for rec in recommendations:
            response_parts.append(f"• {rec}")

    # Parameters used
    target_cols = parameters.get("target_columns", [])
    if target_cols:
        response_parts.append(f"\n**Columnas analizadas:** {', '.join(target_cols)}")

    # Footer
    response_parts.append(
        f"\n---\n**Fuente:** Análisis Polars de Alto Rendimiento | **Timestamp:** {results.get('timestamp', 'N/A')}"
    )

    return "\n".join(response_parts)


def create_polars_analysis_tool() -> StructuredTool:
    """
    Create a LangChain StructuredTool that wraps the Polars data analysis functionality.

    Returns:
        StructuredTool: A LangChain StructuredTool instance for Polars data analysis
    """
    return StructuredTool.from_function(
        func=polars_data_analysis_tool,
        name="polars_data_analysis",
        description="""
Perform high-performance analysis on tabular data using Polars.

Supported analysis types (only these four):
- overview: Descriptive summary + distributions + data quality
- performance: Rankings, group comparisons, outliers, performance gaps
- trends: Temporal trends, seasonality, and forecasting
- relationships: Correlations, regressions, and variable dependencies

Provide tabular data (markdown table, CSV, or JSON) and specify the analysis_type.
        """,
        args_schema=PolarsAnalysisInput,
    )


# NEW FORMATTING FUNCTIONS FOR SIMPLIFIED ANALYSIS TYPES
def _format_overview_results(analysis: Dict[str, Any]) -> List[str]:
    """Format overview analysis results (descriptive + distribution + quality)"""
    results = []

    # Dataset summary
    summary = analysis.get("summary", {})
    total_rows = summary.get("total_rows", 0)
    size_category = summary.get("dataset_size_category", "Unknown")

    results.append(f"\n### 📋 Resumen del Dataset")
    results.append(f"**Tamaño:** {total_rows:,} filas ({size_category})")
    results.append(f"**Columnas analizadas:** {summary.get('numeric_columns_analyzed', 0)}")
    
    # Business totals (non-temporal numeric columns)
    totals = analysis.get("business_totals", {})
    if isinstance(totals, dict) and totals:
        results.append("\n### Σ Totales por Métrica (no temporales)")
        for col, val in totals.items():
            try:
                results.append(f"• {col}: {float(val):,.2f}")
            except Exception:
                results.append(f"• {col}: {val}")
    
    # Cross-column statistical summary
    cross_column = analysis.get("cross_column_analysis", {})
    stats_summary = cross_column.get("statistical_summary", {})

    if stats_summary:
        results.append("\n### 🎯 Resumen Estadístico Global")
        avg_mean = stats_summary.get("mean_of_means", 0)
        avg_cv = stats_summary.get("avg_coefficient_of_variation", 0)
        avg_skew = stats_summary.get("avg_skewness", 0)
        avg_kurt = stats_summary.get("avg_kurtosis", 0)

        results.append(f"**Promedio de medias:** {avg_mean:.2f}")
        results.append(f"**Variabilidad promedio:** {avg_cv:.3f}")
        results.append(
            f"**Asimetría promedio:** {avg_skew:.3f} | **Curtosis promedio:** {avg_kurt:.3f}"
        )

        most_variable = stats_summary.get("most_variable_column")
        most_stable = stats_summary.get("most_stable_column")

        if most_variable:
            results.append(f"**Más variable:** {most_variable}")
        if most_stable:
            results.append(f"**Más estable:** {most_stable}")

    # Detailed statistics per column
    desc_stats = analysis.get("descriptive_stats", {})
    if desc_stats:
        results.append("\n### 📊 Estadísticas Detalladas por Columna")
        for col, stats in list(desc_stats.items())[:4]:  # Top 4 columns
            if isinstance(stats, dict) and "mean" in stats:
                results.append(f"\n#### 📈 {col}")

                # Central tendency measures
                mean = stats.get("mean", 0)
                median = stats.get("median", 0)
                mode = stats.get("mode")

                results.append(
                    f"**Tendencia Central:** Media={mean:.2f}, Mediana={median:.2f}"
                )
                if mode is not None:
                    mode_freq = stats.get("mode_frequency", 0)
                    results.append(f"**Moda:** {mode} (frecuencia: {mode_freq})")

                # Spread measures
                std = stats.get("std", 0)
                variance = stats.get("variance", 0)
                iqr = stats.get("iqr", 0)
                range_val = stats.get("range", 0)

                results.append(
                    f"**Dispersión:** Desv.Std={std:.2f}, Varianza={variance:.2f}"
                )
                results.append(
                    f"**Rango:** {range_val:.2f} | **RIC (Q3-Q1):** {iqr:.2f}"
                )

                # Quartiles
                q1 = stats.get("q1", 0)
                q3 = stats.get("q3", 0)
                results.append(f"**Cuartiles:** Q1={q1:.2f}, Q3={q3:.2f}")

                # Shape measures
                skewness = stats.get("skewness", 0)
                kurtosis = stats.get("kurtosis", 0)
                results.append(
                    f"**Forma:** Asimetría={skewness:.3f}, Curtosis={kurtosis:.3f}"
                )

                # Shape interpretation
                if abs(skewness) > 1:
                    skew_dir = "derecha" if skewness > 0 else "izquierda"
                    results.append(f"  ↳ Sesgada hacia la {skew_dir}")

                if kurtosis > 1:
                    results.append(f"  ↳ Colas más pesadas que distribución normal")
                elif kurtosis < -1:
                    results.append(f"  ↳ Colas más ligeras que distribución normal")

                # Variability assessment
                cv = stats.get("coefficient_of_variation", 0)
                if cv:
                    if cv > 1.5:
                        variability = "Muy Alta"
                    elif cv > 1:
                        variability = "Alta"
                    elif cv > 0.3:
                        variability = "Media"
                    else:
                        variability = "Baja"
                    results.append(f"**Variabilidad:** {variability} (CV={cv:.3f})")

                # Data quality for this column
                null_pct = stats.get("null_percentage", 0)
                if null_pct > 0:
                    results.append(f"**Calidad:** {null_pct:.1f}% valores nulos")

    # Enhanced data quality summary
    data_quality = analysis.get("data_quality", {})
    quality_metrics = data_quality.get("quality_metrics", {})
    issues_found = data_quality.get("issues_found", 0)

    if issues_found > 0 or quality_metrics:
        results.append("\n### ⚠️ Análisis de Calidad de Datos")

        if issues_found > 0:
            results.append(f"**Problemas detectados:** {issues_found}")
            issues = data_quality.get("issues", [])
            for issue in issues[:3]:  # Top 3 issues
                results.append(f"• {issue}")

        # Quality metrics details
        high_null = quality_metrics.get("high_null_columns", [])
        high_var = quality_metrics.get("high_variability_columns", [])
        skewed = quality_metrics.get("skewed_columns", [])
        outlier_prone = quality_metrics.get("outlier_prone_columns", [])

        if high_null:
            results.append(f"**Columnas con muchos nulos:** {len(high_null)}")
        if high_var:
            results.append(f"**Columnas muy variables:** {len(high_var)}")
        if skewed:
            results.append(f"**Columnas sesgadas:** {len(skewed)}")
        if outlier_prone:
            results.append(f"**Propensas a valores atípicos:** {len(outlier_prone)}")

    # Statistical insights
    statistical_insights = analysis.get("statistical_insights", [])
    if statistical_insights:
        results.append("\n### 🔍 Insights Estadísticos")
        for insight in statistical_insights[:5]:  # Top 5 insights
            results.append(f"• {insight}")

    # Distribution shapes summary
    distributions = analysis.get("distributions", {})
    if distributions:
        results.append("\n### 📈 Resumen de Distribuciones")
        for col, dist_info in list(distributions.items())[:4]:  # Top 4 columns
            if isinstance(dist_info, dict):
                shape = dist_info.get("distribution_shape", "N/A")
                skew = dist_info.get("skewness", 0)
                kurt = dist_info.get("kurtosis", 0)
                results.append(
                    f"**{col}:** {shape} (asimetría={skew:.2f}, curtosis={kurt:.2f})"
                )

    return results


def _format_performance_results(analysis: Dict[str, Any]) -> List[str]:
    """Format performance analysis results (rankings + comparisons + outliers)"""
    results = []

    # Performance summary
    perf_summary = analysis.get("performance_summary", {})
    total_outliers = perf_summary.get("total_outliers", 0)
    cols_with_outliers = perf_summary.get("columns_with_outliers", 0)
    significant_gaps = perf_summary.get("significant_performance_gaps", [])

    results.append("\n### 📊 Resumen de Rendimiento")
    results.append(
        f"**Valores atípicos detectados:** {total_outliers} en {cols_with_outliers} columnas"
    )
    if significant_gaps:
        results.append(
            f"**Brechas significativas de rendimiento:** {len(significant_gaps)}"
        )
        for gap in significant_gaps[:3]:  # Top 3 gaps
            analysis_name = gap.get("analysis", "N/A")
            gap_pct = gap.get("gap_pct", 0)
            results.append(f"  • {analysis_name}: {gap_pct:.1f}%")

    # Top rankings
    rankings = analysis.get("rankings", {})
    if rankings:
        results.append("\n### 🏆 Top Performers")
        for col, ranking_info in list(rankings.items())[:2]:  # Top 2 columns
            if isinstance(ranking_info, dict) and "top_performers" in ranking_info:
                top_performers = ranking_info.get("top_performers", [])[:3]
                if top_performers:
                    results.append(f"\n**{col}:**")
                    for i, performer in enumerate(top_performers, 1):
                        value = performer.get(col, 0)
                        results.append(f"  {i}. {value:,.2f}")

    # Comparisons summary
    comparisons = analysis.get("comparisons", {})
    if comparisons:
        results.append("\n### ⚖️ Análisis Comparativo")
        for comparison_name, data in list(comparisons.items())[:2]:  # Top 2 comparisons
            if isinstance(data, dict) and "groups" in data:
                groups = data.get("groups", [])[:3]  # Top 3 groups
                if groups:
                    results.append(
                        f"\n**{comparison_name.replace('_by_', ' por ').title()}:**"
                    )
                    for i, group in enumerate(groups, 1):
                        # Get the group identifier and value
                        group_keys = [
                            k
                            for k in group.keys()
                            if k
                            not in [
                                "value",
                                "count",
                                "mean",
                                "std",
                                "min",
                                "max",
                                "percentage_of_total",
                                "performance_vs_mean",
                            ]
                        ]
                        if group_keys:
                            group_name = group[group_keys[0]]
                            value = group.get("value", 0)
                            percentage = group.get("percentage_of_total", 0)
                            results.append(
                                f"  {i}. {group_name}: {value:,.0f} ({percentage:.1f}%)"
                            )

    return results


def _format_trends_results(analysis: Dict[str, Any]) -> List[str]:
    """Format trends analysis results (comprehensive temporal analysis)
    Rules:
    - Do NOT report trends or forecasts for temporal columns (e.g., 'mes', 'anio').
    - Seasonality should refer to business metrics (ventas, kilos), not the 'mes' column itself.
    - Safe filtering and deduping of irrelevant items.
    """
    results = []

    temporal_cols = {
        "anio",
        "mes",
        "trimestre",
        "quarter",
        "semana",
        "week",
        "dia",
        "day",
    }

    # Trend summary
    trend_summary = analysis.get("trend_summary", {})
    growing_metrics_raw = trend_summary.get("growing_metrics", [])
    declining_metrics_raw = trend_summary.get("declining_metrics", [])
    stable_metrics_raw = trend_summary.get("stable_metrics", [])
    high_volatility_raw = trend_summary.get("high_volatility_metrics", [])
    seasonal_patterns_raw = trend_summary.get("seasonal_patterns_detected", [])

    # Helper: normalize metric entry to a name and filter out temporal/blank
    def _metric_name(item: Any) -> str:
        if isinstance(item, dict):
            return str(item.get("metric", "")).strip()
        return str(item).strip()

    def _not_temporal_metric(item: Any) -> bool:
        name = _metric_name(item)
        return bool(name) and name not in temporal_cols

    def _fmt_pct_signed(v: Optional[float]) -> str:
        try:
            return f"{float(v):+,.1f}%" if v is not None else ""
        except Exception:
            return ""

    def _metric_with_evidence(item: Any) -> str:
        """Return metric name with numeric evidence (MoM avg and/or YoY latest) when available."""
        name = _metric_name(item)
        if not isinstance(item, dict):
            return name
        mom = item.get("avg_mom_pct")
        yoy = item.get("latest_yoy_pct")
        parts = []
        if mom is not None:
            parts.append(f"MoM prom: {_fmt_pct_signed(mom)}")
        if yoy is not None:
            parts.append(f"YoY últ: {_fmt_pct_signed(yoy)}")
        return f"{name} (" + "; ".join(parts) + ")" if parts else name

    # Filter and normalize lists
    growing_metrics = [m for m in growing_metrics_raw if _not_temporal_metric(m)]
    declining_metrics = [m for m in declining_metrics_raw if _not_temporal_metric(m)]
    stable_metrics = [m for m in stable_metrics_raw if _not_temporal_metric(m)]
    high_volatility = [m for m in high_volatility_raw if _not_temporal_metric(m)]
    seasonal_patterns = [_metric_name(m) for m in seasonal_patterns_raw if _not_temporal_metric(m)]

    results.append("\n### 📊 Resumen de Tendencias")

    # Summaries only for business metrics
    if growing_metrics:
        results.append(
            f"\n**📈 Métricas con Tendencia Creciente:** "
            + ", ".join([_metric_with_evidence(m) for m in growing_metrics[:5]])
        )

    if declining_metrics:
        results.append(
            f"\n**📉 Métricas con Tendencia Decreciente:** "
            + ", ".join([_metric_with_evidence(m) for m in declining_metrics[:5]])
        )

    if stable_metrics:
        stable_metric_names = [_metric_name(m) for m in stable_metrics[:5]]
        if stable_metric_names:
            results.append(
                f"\n**➡️ Métricas Estables:** " + ", ".join(stable_metric_names)
            )

    if seasonal_patterns:
        results.append(
            f"\n**🔄 Patrones Estacionales (por métrica):** "
            + ", ".join(seasonal_patterns)
        )

    # Forecasting section with actual values (for business metrics only)
    forecast_indicators = analysis.get("forecast_indicators", {})
    forecasts = analysis.get("forecasts", {})
    temporal_analysis_map = analysis.get("temporal_analysis", {})

    def _build_trend_text(col: str) -> str:
        ti = temporal_analysis_map.get(col, {}) if isinstance(temporal_analysis_map, dict) else {}
        direction = str(ti.get("trend_direction", "N/A")).title()
        mom = ti.get("avg_mom_change_pct")
        yoy = ti.get("yoy_change_pct")
        parts = []
        if mom is not None:
            parts.append(f"MoM prom: {_fmt_pct_signed(mom)}")
        if yoy is not None:
            parts.append(f"YoY últ: {_fmt_pct_signed(yoy)}")
        if parts:
            return f"{direction} ({'; '.join(parts)})"
        return direction

    if forecast_indicators or forecasts:
        results.append(f"\n### 🔮 PRONÓSTICOS Y PROYECCIONES")

        # High confidence forecasts (filter temporal)
        high_confidence = [
            col
            for col, indicators in forecast_indicators.items()
            if indicators.get("forecast_confidence") == "alta"
            and col not in temporal_cols
        ]
        if high_confidence:
            results.append(
                f"\n**🎯 Alta Confianza ({len(high_confidence)} métricas):**"
            )
            for col in high_confidence[:3]:  # Top 3
                indicators = forecast_indicators[col]
                forecast_data = forecasts.get(col, {})

                periods = indicators.get("recommended_periods", 0)
                trend_text = _build_trend_text(col)

                # Show enhanced forecast values with 95% confidence intervals
                if forecast_data.get("values"):
                    next_values = forecast_data["values"][:3]  # Next 3 periods
                    methods = forecast_data.get("methods_used", [])
                    upper_bounds = forecast_data.get("upper_bounds", [])[:3]
                    lower_bounds = forecast_data.get("lower_bounds", [])[:3]
                    confidence_info = forecast_data.get("confidence_intervals", {})
                    explanations = forecast_data.get("explanation", {})

                    results.append(f"• **{col}** (Tendencia {trend_text})")

                    if (
                        upper_bounds
                        and lower_bounds
                        and len(upper_bounds) == len(next_values)
                    ):
                        values_with_ranges = []
                        for i, val in enumerate(next_values):
                            values_with_ranges.append(
                                f"{val:,.0f} (rango: {lower_bounds[i]:,.0f}-{upper_bounds[i]:,.0f})"
                            )
                        values_str = ", ".join(values_with_ranges)
                        confidence_level = confidence_info.get(
                            "confidence_level", "95%"
                        )
                        results.append(f"  - Próximos valores: {values_str}")
                        results.append(
                            f"  - Intervalos de confianza: {confidence_level}"
                        )
                    else:
                        values_str = ", ".join([f"{v:.2f}" for v in next_values])
                        results.append(f"  - Próximos valores: {values_str}")

                    if methods:
                        methods_str = ", ".join(methods)
                        results.append(f"  - Métodos: {methods_str}")

                    if explanations.get("resumen_ejecutivo"):
                        exec_summary = explanations["resumen_ejecutivo"]
                        exec_summary = exec_summary.replace("📈 PRONÓSTICO PARA ", "")
                        if len(exec_summary) > 200:
                            exec_summary = exec_summary[:200] + "..."
                        results.append(f"  - Resumen: {exec_summary}")
                else:
                    results.append(
                        f"• **{col}**: Tendencia {trend_text} - Recomendado {periods} períodos"
                    )

        # Medium confidence forecasts (filter temporal)
        medium_confidence = [
            col
            for col, indicators in forecast_indicators.items()
            if indicators.get("forecast_confidence") == "media"
            and col not in temporal_cols
        ]
        if medium_confidence:
            results.append(
                f"\n**📊 Confianza Media ({len(medium_confidence)} métricas):**"
            )
            for col in medium_confidence[:3]:  # Top 3
                indicators = forecast_indicators[col]
                forecast_data = forecasts.get(col, {})

                periods = indicators.get("recommended_periods", 0)
                trend_text = _build_trend_text(col)

                if forecast_data.get("values"):
                    next_values = forecast_data["values"][:3]
                    methods = forecast_data.get("methods_used", [])
                    upper_bounds = forecast_data.get("upper_bounds", [])[:3]
                    lower_bounds = forecast_data.get("lower_bounds", [])[:3]
                    confidence_info = forecast_data.get("confidence_intervals", {})
                    explanations = forecast_data.get("explanation", {})

                    results.append(f"• **{col}** (Tendencia {trend_text})")

                    if (
                        upper_bounds
                        and lower_bounds
                        and len(upper_bounds) == len(next_values)
                    ):
                        values_with_ranges = []
                        for i, val in enumerate(next_values):
                            values_with_ranges.append(
                                f"{val:,.0f} (rango: {lower_bounds[i]:,.0f}-{upper_bounds[i]:,.0f})"
                            )
                        values_str = ", ".join(values_with_ranges)
                        confidence_level = confidence_info.get(
                            "confidence_level", "95%"
                        )
                        results.append(f"  - Próximos valores: {values_str}")
                        results.append(
                            f"  - Intervalos de confianza: {confidence_level}"
                        )
                    else:
                        values_str = ", ".join([f"{v:.1f}" for v in next_values])
                        results.append(f"  - Próximos valores: {values_str}")

                    if methods:
                        methods_str = ", ".join(methods)
                        results.append(f"  - Métodos: {methods_str}")

                    if explanations.get("metodologia"):
                        methodology = explanations["metodologia"]
                        if "ensemble de múltiples métodos" in methodology:
                            results.append(
                                f"  - Método: Ensemble de múltiples métodos con intervalos de confianza del 95%"
                            )
                else:
                    results.append(
                        f"• **{col}**: Tendencia {trend_text}, Proyección {periods} períodos"
                    )

        # Low confidence forecasts (filter temporal)
        low_confidence = [
            col
            for col, indicators in forecast_indicators.items()
            if indicators.get("forecast_confidence") == "baja"
            and col not in temporal_cols
        ]
        if low_confidence:
            results.append(f"\n**⚠️ Confianza Baja ({len(low_confidence)} métricas):**")
            for col in low_confidence[:2]:
                indicators = forecast_indicators[col]
                forecast_data = forecasts.get(col, {})

                periods = indicators.get("recommended_periods", 0)
                trend_text = _build_trend_text(col)

                if forecast_data.get("values"):
                    next_value = (
                        forecast_data["values"][0] if forecast_data["values"] else "N/A"
                    )
                    results.append(
                        f"• **{col}** (Tendencia {trend_text}): Próximo valor estimado {next_value:,.0f}"
                    )
                else:
                    results.append(
                        f"• **{col}**: Tendencia {trend_text}, proyección {periods} períodos"
                    )
    

    # New: Per-product trend highlights (Top & Bottom 3) using precomputed per_product_analysis
    ta = analysis.get("temporal_analysis", {})
    if isinstance(ta, dict) and ta:
        results.append("\n### 🏆 Tendencias por Producto (Top y Bottom 3)")
        # Determine priority business metrics
        all_cols = list(ta.keys())
        business_cols = [c for c in all_cols if c and c not in temporal_cols]
        priority_order = ["total_ventas_usd", "total_kilos", "total_kilos_vendidos"]
        priority = [c for c in priority_order if c in business_cols]
        for c in business_cols:
            if c not in priority:
                priority.append(c)

        def _fmt_pct(v: Optional[float]) -> str:
            try:
                return "N/A" if v is None else f"{float(v):+.1f}%"
            except Exception:
                return "N/A"

        # Limit to first two key metrics to keep output concise
        for col in priority[:2]:
            trend_info = ta.get(col, {})
            if not isinstance(trend_info, dict):
                continue
            ppa = trend_info.get("per_product_analysis")
            if not isinstance(ppa, dict):
                continue

            product_col = ppa.get("product_column_used", "Producto")
            results.append(f"\n#### 📦 {col}")
            results.append(f"Productos analizados: {ppa.get('total_products_analyzed', 0)} | Columna: {product_col}")

            top = ppa.get("top_3_products", {})
            bottom = ppa.get("bottom_3_products", {})
            mtr = ppa.get("monthly_trends", {})
            ytr = ppa.get("yearly_trends", {})

            def _find_total(details: List[Dict[str, Any]], name: str) -> float:
                for d in details or []:
                    try:
                        if d.get(product_col) == name:
                            return float(d.get("total_value", 0))
                    except Exception:
                        continue
                return 0.0

            def _get_latest(product: str, which: str) -> (Optional[float], Optional[float]):
                # returns (mom, yoy)
                try:
                    if which == "top":
                        if isinstance(mtr, dict) and mtr.get("top_3", {}).get(product):
                            t = mtr["top_3"][product]
                            return t.get("latest_mom_change_pct"), t.get("latest_yoy_change_pct")
                        if isinstance(ytr, dict) and ytr.get("top_3", {}).get(product):
                            t = ytr["top_3"][product]
                            return None, t.get("latest_yoy_change_pct")
                    else:
                        if isinstance(mtr, dict) and mtr.get("bottom_3", {}).get(product):
                            t = mtr["bottom_3"][product]
                            return t.get("latest_mom_change_pct"), t.get("latest_yoy_change_pct")
                        if isinstance(ytr, dict) and ytr.get("bottom_3", {}).get(product):
                            t = ytr["bottom_3"][product]
                            return None, t.get("latest_yoy_change_pct")
                except Exception:
                    return None, None
                return None, None

            # Top 3 block
            top_products = top.get("products", [])
            top_details = top.get("details", [])
            if top_products:
                results.append("\nTop 3:")
                for i, p in enumerate(top_products, 1):
                    total_val = _find_total(top_details, p)
                    mom, yoy = _get_latest(p, "top")
                    results.append(
                        f"  {i}. {p}: total={total_val:,.0f} | MoM último={_fmt_pct(mom)} | YoY último={_fmt_pct(yoy)}"
                    )

            # Bottom 3 block
            bottom_products = bottom.get("products", [])
            bottom_details = bottom.get("details", [])
            if bottom_products:
                results.append("\nBottom 3:")
                for i, p in enumerate(bottom_products, 1):
                    total_val = _find_total(bottom_details, p)
                    mom, yoy = _get_latest(p, "bottom")
                    results.append(
                        f"  {i}. {p}: total={total_val:,.0f} | MoM último={_fmt_pct(mom)} | YoY último={_fmt_pct(yoy)}"
                    )

    # Detailed temporal analysis (business metrics only)
    temporal_analysis = analysis.get("temporal_analysis", {})
    if temporal_analysis:
        results.append("\n### 📅 ANÁLISIS TEMPORAL DETALLADO")

        all_cols = list(temporal_analysis.keys())
        # Business metrics only (exclude temporal columns and blanks)
        business_cols = [c for c in all_cols if c and c not in temporal_cols]

        # Prioritize common business metrics first
        priority_order = ["total_ventas_usd", "total_kilos", "total_kilos_vendidos"]
        priority = [c for c in priority_order if c in business_cols]
        for c in business_cols:
            if c not in priority:
                priority.append(c)

        if not priority:
            results.append(
                "No hay métricas numéricas de negocio para análisis temporal."
            )
        else:
            for col in priority:
                trend_info = temporal_analysis.get(col)
                if not isinstance(trend_info, dict):
                    continue

                results.append(f"\n#### 📈 {col}")

                direction = trend_info.get("trend_direction", "N/A")
                volatility = trend_info.get("volatility_level", "N/A")
                vol_value = trend_info.get("volatility", None)
                mom_avg = trend_info.get("avg_mom_change_pct")
                yoy_last = trend_info.get("yoy_change_pct")

                # Build trend evidence text
                evidence_parts = []
                if mom_avg is not None:
                    try:
                        evidence_parts.append(f"MoM prom: {float(mom_avg):+,.1f}%")
                    except Exception:
                        pass
                if yoy_last is not None:
                    try:
                        evidence_parts.append(f"YoY últ: {float(yoy_last):+,.1f}%")
                    except Exception:
                        pass
                trend_line = f"**Tendencia:** {str(direction).title()}"
                if evidence_parts:
                    trend_line += " (" + "; ".join(evidence_parts) + ")"

                # Build volatility text with numeric value if available
                vol_line = f"**Volatilidad:** {str(volatility).title()}"
                try:
                    if vol_value is not None:
                        vol_line += f" ({float(vol_value)*100:,.1f}%)"
                except Exception:
                    pass

                results.append(f"{trend_line} | {vol_line}")

                # Full MoM series
                mom_series = trend_info.get("mom_series")
                if isinstance(mom_series, dict) and mom_series:
                    is_per_year = any(isinstance(v, dict) for v in mom_series.values())
                    if is_per_year:
                        results.append(
                            "\n**Serie MoM por mes (vs mes anterior, por año):**"
                        )
                        for y in sorted(mom_series.keys()):
                            series = mom_series.get(y, {})
                            if isinstance(series, dict) and series:
                                parts = []
                                for m in sorted(series.keys()):
                                    try:
                                        parts.append(f"Mes {int(m)}: {series[m]:+.1f}%")
                                    except Exception:
                                        continue
                                if parts:
                                    results.append(
                                        f"• Año {int(y)}: " + ", ".join(parts)
                                    )
                    else:
                        parts = []
                        for m in sorted(mom_series.keys()):
                            try:
                                parts.append(f"Mes {int(m)}: {mom_series[m]:+.1f}%")
                            except Exception:
                                continue
                        if parts:
                            results.append(
                                "\n**Serie MoM por mes:** " + ", ".join(parts)
                            )

                # Full YoY series (only if multi-year)
                yoy_series = trend_info.get("yoy_series")
                if isinstance(yoy_series, dict) and yoy_series:
                    results.append("\n**Serie YoY por mes (cada año vs año previo):**")
                    for y in sorted(yoy_series.keys()):
                        series = yoy_series.get(y, {})
                        if isinstance(series, dict) and series:
                            parts = []
                            for m in sorted(series.keys()):
                                try:
                                    parts.append(f"Mes {int(m)}: {series[m]:+.1f}%")
                                except Exception:
                                    continue
                            if parts:
                                results.append(f"• Año {int(y)}: " + ", ".join(parts))

                # Same-month YoY (latest vs. previous year)
                same_months_yoy = trend_info.get("same_months_yoy")
                if isinstance(same_months_yoy, dict) and same_months_yoy:
                    results.append(
                        "\n**Comparación interanual por mes (año más reciente vs. anterior):**"
                    )
                    for m in sorted(same_months_yoy.keys()):
                        try:
                            mv = same_months_yoy[m]
                            results.append(f"• Mes {int(m)}: {mv:+.1f}%")
                        except Exception:
                            continue
                elif not yoy_series:
                    results.append(
                        "\n**Nota YoY:** Para análisis año-sobre-año se requieren datos de múltiples años"
                    )

                # Seasonality flag only as part of the metric's narrative
                if trend_info.get("seasonality_detected", False):
                    details = trend_info.get("seasonality_details")
                    strength = trend_info.get("seasonality_strength")
                    if isinstance(details, dict) and (
                        details.get("high_ranges") or details.get("low_ranges")
                    ):
                        line = "**🔄 Estacionalidad detectada**"
                        if strength:
                            line += f" ({strength})"
                        results.append(line)
                        parts = []
                        high_ranges = details.get("high_ranges") or []
                        low_ranges = details.get("low_ranges") or []
                        if high_ranges:
                            parts.append(f"Altos: {', '.join(high_ranges)}")
                        if low_ranges:
                            parts.append(f"Bajos: {', '.join(low_ranges)}")
                        if parts:
                            results.append("  - " + " | ".join(parts))
                    else:
                        results.append("**🔄 Estacionalidad detectada**")

    return results


def _format_relationships_results(analysis: Dict[str, Any]) -> List[str]:
    """Format relationships analysis results (correlations + regressions)
    Policy:
    - If there are no significant/strong correlations, return a minimal message and omit health or network scores.
    """
    results = []

    # Relationship summary
    relationship_summary = analysis.get("relationship_summary", {})
    total_correlations = relationship_summary.get("total_correlations_found", 0)
    significant_relationships = relationship_summary.get("significant_relationships", 0)
    strong_relationships = relationship_summary.get("strong_relationships", 0)

    correlations = analysis.get("correlations", {})
    significant_corrs = correlations.get("significant_correlations", [])

    # Minimal output if nothing meaningful
    if (
        significant_relationships == 0 and strong_relationships == 0
    ) or not significant_corrs:
        results.append(
            "No se observaron relaciones fuertes entre las métricas analizadas."
        )
        return results

    # Otherwise, print a concise but useful summary
    results.append("\n### 📊 Resumen de Relaciones")
    results.append(f"**Relaciones significativas:** {significant_relationships}")
    results.append(f"**Relaciones fuertes:** {strong_relationships}")

    # Significant correlations
    if significant_corrs:
        results.append("\n### 🔗 Correlaciones Significativas")
        for corr in significant_corrs[:5]:  # Top 5
            vars_name = corr.get("variables", "")
            correlation = corr.get("correlation", 0)
            interpretation = corr.get("interpretation", "")

            strength_icon = (
                "🔴" if correlation < -0.7 else "🟢" if correlation > 0.7 else "🟡"
            )
            results.append(
                f"{strength_icon} **{vars_name}**: {correlation:.3f} - {interpretation}"
            )

    # Regression results (optional, include if present)
    regressions = analysis.get("regressions", {})
    if regressions:
        results.append("\n### 📈 Análisis de Regresión")
        for reg_name, reg_info in list(regressions.items())[:3]:  # Top 3 regressions
            if isinstance(reg_info, dict):
                correlation = reg_info.get("correlation", 0)
                r_squared = reg_info.get("r_squared", 0)
                strength = reg_info.get("relationship_strength", "N/A")

                clean_name = reg_name.replace("_predicts_", " → ")
                results.append(f"\n**{clean_name}:**")
                results.append(
                    f"  Correlación: {correlation:.3f} | R²: {r_squared:.3f} | Fuerza: {strength}"
                )

    return results


polars_analysis_tool = create_polars_analysis_tool()
