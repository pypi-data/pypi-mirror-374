#!/usr/bin/env python3
"""
Test that EnhancedSalesAgent deterministically consumes DATA_JSON_KEY and calls the Polars tool via data_ref,
producing a RESPUESTA FINAL without asking for more data.
"""

import json
import pytest
from langchain_core.messages import AIMessage

from utils.data_registry import register_data, clear as registry_clear
from agents.analista_ventas import sales_agent


@pytest.fixture(autouse=True)
def _clear_registry():
    registry_clear()
    yield
    registry_clear()


def test_sales_agent_short_circuits_on_data_key():
    # Prepare a small monthly dataset
    rows = [
        {"anio": 2022, "mes": 1, "total_ventas_usd": 120000.0, "total_kilos_vendidos": 7000.0},
        {"anio": 2022, "mes": 2, "total_ventas_usd": 130000.0, "total_kilos_vendidos": 7100.0},
    ]
    key = register_data(json.dumps(rows))

    # Fake last message from text_sql with DATA_JSON_KEY
    content = f"DATA_JSON_KEY:\n{key}\n\n**Fuente de datos consultada:** Test Source"
    state = {"messages": [AIMessage(content=content, name="text_sql")]} 

    result = sales_agent.invoke(state)
    msgs = result.get("messages", [])
    assert msgs, "Agent should return a message"
    out = msgs[-1].content
    assert out.startswith("RESPUESTA FINAL"), "Should produce a final response immediately"
    assert "ANÁLISIS DE DATOS AVANZADO" in out, "Should include analysis output"
    assert "FUENTE DE DATOS: \"Databricks Sell-In\"" in out, "Should include data source line"
