#!/usr/bin/env python3
"""
Tests for robust parsing and analysis using Polars utilities and tool wrapper.
Covers markdown with pandas-style index column, CSV, JSON with wrappers, and
flexible fallback parsing, plus end-to-end tool execution using data_ref.
"""

import json
import pytest

from utils.polars_analytics import parse_tabular_data, analyze_data
from utils.lazy_load import get_polars
from utils.data_registry import register_data, clear as registry_clear
from tools.polars_data_tool import polars_data_analysis_tool


@pytest.fixture(autouse=True)
def _clear_registry():
    # Ensure registry is clean between tests
    registry_clear()
    yield
    registry_clear()


def test_markdown_pandas_index_parses_and_temporal():
    md = (
        "|    | anio | mes | total_ventas_usd | total_kilos_vendidos |\n"
        "|---:|----:|----:|-------------------:|-----------------------:|\n"
        "|  0 | 2022 | 12 | 1.23e6 | 90000 |\n"
        "|  1 | 2023 |  1 | 1450000 | 100500 |\n"
        "|  2 | 2023 |  2 | 1.30E6 | 98750 |\n"
    )

    df = parse_tabular_data(md)
    assert df is not None, "Markdown with index should parse"
    assert set(["anio", "mes", "total_ventas_usd", "total_kilos_vendidos"]).issubset(set(df.columns))
    assert df.height == 3
    # Types: year/month numeric
    pl = get_polars()
    assert df["anio"].dtype in (pl.Int64, pl.Int32, pl.Float64, pl.Float32)
    assert df["mes"].dtype in (pl.Int64, pl.Int32, pl.Float64, pl.Float32)

    # Trends analysis (replaces legacy temporal)
    res = analyze_data(df, analysis_type="trends", target_columns=["total_ventas_usd"], time_column="mes")
    assert "analysis" in res and isinstance(res["analysis"], dict)
    assert "temporal_analysis" in res["analysis"]
    assert "total_ventas_usd" in res["analysis"]["temporal_analysis"]


def test_flexible_parser_without_separator_line():
    # No alignment row, should fall back to flexible parser
    md = (
        "| anio | mes | total_ventas_usd |\n"
        "| 2024 |  1  | 250000 |\n"
        "| 2024 |  2  | 260000 |\n"
    )
    df = parse_tabular_data(md)
    assert df is not None, "Flexible parser should handle header without separator"
    assert set(["anio", "mes", "total_ventas_usd"]).issubset(set(df.columns))
    assert df.height == 2


def test_json_array_with_prefix_and_code_fence():
    payload = [
        {"anio": 2023, "mes": 11, "total_ventas_usd": 500000.0, "total_kilos_vendidos": 30000.0},
        {"anio": 2023, "mes": 12, "total_ventas_usd": 600000.0, "total_kilos_vendidos": 35000.0},
    ]
    wrapped = "DATA_JSON:\n```json\n" + json.dumps(payload) + "\n```"
    df = parse_tabular_data(wrapped)
    assert df is not None, "JSON array wrapped should parse"
    assert df.height == 2
    assert set(["anio", "mes", "total_ventas_usd", "total_kilos_vendidos"]).issubset(set(df.columns))


def test_csv_parses():
    csv_data = (
        "anio,mes,total_ventas_usd,total_kilos_vendidos\n"
        "2022,7,123456.78,45000\n"
        "2022,8,130000.00,47000\n"
    )
    df = parse_tabular_data(csv_data)
    assert df is not None, "CSV should parse"
    assert df.height == 2


def test_polars_data_tool_with_data_ref_end_to_end():
    rows = [
        {"anio": 2024, "mes": 5, "total_ventas_usd": 420000.0, "total_kilos_vendidos": 25000.0},
        {"anio": 2024, "mes": 6, "total_ventas_usd": 460000.0, "total_kilos_vendidos": 27000.0},
        {"anio": 2024, "mes": 7, "total_ventas_usd": 480000.0, "total_kilos_vendidos": 28000.0},
    ]
    key = register_data(json.dumps(rows))

    # Overview
    out_desc = polars_data_analysis_tool(
        raw_data="",
        data_ref=key,
        analysis_type="overview",
        target_columns="total_ventas_usd,total_kilos_vendidos",
    )
    assert isinstance(out_desc, str)
    assert "ANÁLISIS DE DATOS AVANZADO" in out_desc
    assert "RESUMEN GENERAL" in out_desc
    
    # Trends
    out_temp = polars_data_analysis_tool(
        raw_data="",
        data_ref=key,
        analysis_type="trends",
        time_column="mes",
        target_columns="total_ventas_usd,total_kilos_vendidos",
    )
    assert isinstance(out_temp, str)
    assert "ANÁLISIS DE TENDENCIAS" in out_temp
