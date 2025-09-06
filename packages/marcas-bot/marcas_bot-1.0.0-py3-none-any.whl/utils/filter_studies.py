import json
import os
from typing import Any, Dict, List, Optional, Tuple

import requests
from config.params import DATABRICKS_HOST, DATABRICKS_TOKEN, DATABRICKS_WAREHOUSE_ID
from utils.logger import logger

# ---------------------------
# Input schema (Pydantic)
# ---------------------------
ALLOWED_COUNTRIES = {"NICARAGUA", "INTERNACIONAL"}

# Bounded year regex with two capture groups; year is group 2
# Avoid \d to prevent escaping issues in SQL string.
YEAR_BOUNDED_REGEX = r"(?i)(^|[/_.-])((?:19|20)[0-9]{2})(?=[/_.-]|$)"


# ---------------------------
# SQL builder
# ---------------------------
def _build_sql(
    year: Optional[int],
    year_range: Optional[Tuple[int, int]],
    countries: Optional[List[str]],
    limit: int,
) -> str:
    # Compute year bounds
    y_from: Optional[int] = None
    y_to: Optional[int] = None
    if year is not None:
        y_from = int(year)
        y_to = int(year)
    if year_range is not None:
        a, b = int(year_range[0]), int(year_range[1])
        y_from, y_to = (min(a, b), max(a, b))

    where_clauses: List[str] = []

    # Optional exact path-level guard for single-year queries (prevents false positives)
    if year is not None and year_range is None:
        where_clauses.append(
            f"regexp_like(file_path, '(^|[/_.-]){int(year)}([/_.-]|$)')"
        )

    # Comparisons on extracted integer year (NULL-safe: rows without a year are excluded)
    if y_from is not None and y_to is not None:
        where_clauses.append(f"year >= {y_from} AND year <= {y_to}")
    elif y_from is not None:
        where_clauses.append(f"year >= {y_from}")
    elif y_to is not None:
        where_clauses.append(f"year <= {y_to}")

    if countries:
        # countries normalized to ["Nicaragua"|"Internacional"] -> compare uppercase in SQL
        uppers = [c.upper() for c in countries]
        vals = ", ".join([f"'{u}'" for u in uppers])
        where_clauses.append(f"upper(country) IN ({vals})")

    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    # Cap limit to max 1000
    limit = max(1, min(int(limit), 1000))

    statement = f"""
WITH base AS (
  SELECT
    file_path,
    country,
    TRY_CAST(regexp_extract(file_path, '{YEAR_BOUNDED_REGEX}', 2) AS INT) AS year
  FROM silver.external_data.delisoy_summarized
)
SELECT file_path, country, year
FROM base
{where_sql}
ORDER BY year DESC NULLS LAST, file_path
LIMIT {limit}
"""
    return statement


# ---------------------------
# SQL executor
# ---------------------------
def _execute_sql(statement: str) -> Dict[str, Any]:
    host = DATABRICKS_HOST
    token = DATABRICKS_TOKEN
    warehouse_id = DATABRICKS_WAREHOUSE_ID
    if not host or not token:
        raise RuntimeError(
            "DATABRICKS_HOST and DATABRICKS_TOKEN must be set in environment to run SQL"
        )
    if not warehouse_id:
        raise RuntimeError(
            "DATABRICKS_WAREHOUSE_ID must be set in environment to run SQL statements"
        )

    # Ensure host doesn't already have https:// prefix
    clean_host = host.replace("https://", "") if host.startswith("https://") else host
    url = f"https://{clean_host}/api/2.0/sql/statements"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload: Dict[str, Any] = {
        "warehouse_id": warehouse_id,
        "statement": statement,
        "catalog": "silver",
        "schema": "external_data",
        "wait_timeout": "30s",
        "on_wait_timeout": "CANCEL",
    }

    logger.info(
        "Executing SQL on silver.external_data.delisoy_summarized(sync up to 30s)"
    )
    resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
    resp.raise_for_status()
    data = resp.json()

    status = data.get("status") or data.get("status_code")
    if isinstance(status, dict) and status.get("state") == "FAILED":
        raise RuntimeError(f"SQL failed: {data}")

    return data


# ---------------------------
# Tool function
# ---------------------------
def filter_studies(
    year: Optional[int] = None,
    year_range: Optional[List[int]] = None,  # Changed from Tuple to List
    countries: Optional[List[str]] = None,
    limit: int = 100,
) -> str:
    """
    Filter the summaries table by year (from file_path) and/or country using Databricks SQL.

    Table: {FQN}

    Returns a compact JSON string with rows and row_count. Each row has: file_path, country, year.
    """
    # Log the incoming request with parameters
    filter_parts = []
    if year is not None:
        filter_parts.append(f"year={year}")
    if year_range is not None:
        filter_parts.append(f"year_range={year_range}")
    if countries:
        filter_parts.append(f"countries={countries}")
    filter_parts.append(f"limit={limit}")

    filter_description = ", ".join(filter_parts)
    logger.info(f"Starting SQL filter: {filter_description}")

    try:
        # Convert year_range list to tuple for internal _build_sql usage
        if year_range is not None:
            year_range = tuple(year_range)
            logger.debug(f"Converted year_range to tuple: {year_range}")

        statement = _build_sql(year, year_range, countries, limit)
        logger.debug(f"Generated SQL statement: {statement[:200]}...")

        result = _execute_sql(statement)
        logger.debug(f"SQL execution completed, raw result keys: {list(result.keys())}")

        # Parse Databricks SQL response robustly
        rows: List[Dict[str, Any]] = []

    except Exception as e:
        logger.error(f"SQL execution failed: {str(e)} - {filter_description}")
        return json.dumps(
            {
                "table": "silver.external_data.delisoy_summarized",
                "row_count": 0,
                "rows": [],
                "error": str(e),
            },
            ensure_ascii=False,
        )

    # Parse the SQL response
    try:
        # Primary shape: top-level manifest.schema.columns + result.data_array
        cols: List[str] = []
        data_array: List[List[Any]] = []

        # Try primary shape
        manifest_top = result.get("manifest") or {}
        schema_top = manifest_top.get("schema") or {}
        columns_top = schema_top.get("columns") or []
        if columns_top:
            cols = [c.get("name") for c in columns_top if isinstance(c, dict)]

        result_obj = result.get("result") or {}
        data_array = result_obj.get("data_array") or []

        # Fallback shapes (older/alternative)
        if not cols:
            # Sometimes manifest is nested under result
            manifest_nested = result_obj.get("manifest") or {}
            schema_nested = manifest_nested.get("schema") or {}
            columns_nested = (
                schema_nested.get("columns") or manifest_nested.get("columns") or []
            )
            if columns_nested:
                cols = [
                    c.get("name") if isinstance(c, dict) else str(c)
                    for c in columns_nested
                ]

        if not cols:
            # Another fallback: result.schema.columns and result.data
            schema_res = result_obj.get("schema") or {}
            columns_res = schema_res.get("columns") or []
            if columns_res:
                cols = [c.get("name") for c in columns_res if isinstance(c, dict)]
                data_rows = result_obj.get("data") or []
                if (
                    data_rows
                    and isinstance(data_rows[0], dict)
                    and "row" in data_rows[0]
                ):
                    data_array = [r.get("row") for r in data_rows]

        # Last resort: synthesize column names by position
        if not cols and data_array and isinstance(data_array[0], list):
            cols = [f"col_{i}" for i in range(len(data_array[0]))]

        # Build output rows
        for r in data_array:
            if isinstance(r, list):
                row = {cols[i]: r[i] for i in range(min(len(cols), len(r)))}
                rows.append(
                    {
                        "file_path": row.get("file_path"),
                        "country": row.get("country"),
                        "year": row.get("year"),
                    }
                )

    except Exception as e:
        logger.warning(f"Unexpected SQL result format, returning raw: {e}")
        return json.dumps(result, ensure_ascii=False)

    # Log successful completion with summary
    years_found = set(row.get("year") for row in rows if row.get("year") is not None)
    countries_found = set(row.get("country") for row in rows if row.get("country"))

    result_summary = [f"{len(rows)} rows"]
    if years_found:
        year_list = sorted([y for y in years_found if y is not None])
        result_summary.append(f"years: {year_list}")
    if countries_found:
        result_summary.append(f"countries: {list(countries_found)}")

    logger.info(
        f"SQL filter completed: {', '.join(result_summary)} - {filter_description}"
    )

    # Log sample results at debug level
    if rows:
        logger.debug(f"Sample results (first 3): {rows[:3]}")
    else:
        logger.warning(f"No results found for filter: {filter_description}")

    out = {
        "table": "silver.external_data.delisoy_summarized",
        "row_count": len(rows),
        "rows": rows,
    }
    return json.dumps(out, ensure_ascii=False)
