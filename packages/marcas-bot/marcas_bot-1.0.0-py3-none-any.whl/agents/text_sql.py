from typing import Dict, Any
import re
import json
from config.params import (
    DELISOY_SELL_IN_GENIE_SPACE_ID,
    DATABRICKS_HOST,
    DATABRICKS_TOKEN,
)
from config.prompts import genie_agent_description
from databricks.sdk import WorkspaceClient
from databricks_langchain.genie import GenieAgent
from langchain_core.messages import AIMessage
from utils.logger import logger
from utils.data_registry import register_data


class GenieAgentWithReferences:
    """
    Wrapper around Databricks GenieAgent that automatically adds data source references
    to responses for proper citation in synthesis.
    """
    
    def __init__(self):
        self.genie_agent = GenieAgent(
            genie_space_id=DELISOY_SELL_IN_GENIE_SPACE_ID,
            genie_agent_name="Genie",
            description=genie_agent_description,
            client=WorkspaceClient(host=DATABRICKS_HOST, token=DATABRICKS_TOKEN),
        )
        self.data_source_reference = "Databricks Delisoy Sell-In"
    
    def invoke(self, state: Dict) -> Dict:
        """
        Invoke the Genie agent and automatically append the data source reference.
        Also extract any tabular data for advanced analysis.
        
        Args:
            state: Current conversation state
            
        Returns:
            Dict with updated messages including data response and source reference,
            plus extracted tabular data in state
        """
        # Get the original Genie response
        result = self.genie_agent.invoke(state)
        
        # Extract the messages from the result
        messages = result.get("messages", [])
        if not messages:
            return result
        
        # Get the last message (Genie's response)
        last_message = messages[-1]
        if hasattr(last_message, 'content'):
            original_content = last_message.content
        else:
            # Fallback for different message formats
            original_content = str(last_message)

        # Log the raw, exact output received from Genie before any processing
        try:
            content_len = len(original_content) if isinstance(original_content, str) else -1
            logger.info(
                "=== RAW GENIE MARKDOWN (exact, before parsing) [len=%s] ===\n%s\n=== END RAW GENIE MARKDOWN ===",
                content_len,
                original_content,
            )
        except Exception as e:
            logger.warning(f"Failed to log raw Genie content: {e}")
        
        # Extract tabular data from the response
        extracted_tables = self._extract_tabular_data(original_content)
        # Try to extract SQL query from the original content (if present)
        sql_query = self._extract_sql_query(original_content)

        # Convert to compact monthly JSON (aggregated) when possible
        json_rows = self._to_monthly_json(extracted_tables)

        if json_rows:
            try:
                json_str = json.dumps(json_rows, ensure_ascii=False)
            except Exception as e:
                logger.error(f"Failed to serialize JSON rows: {e}")
                json_str = "[]"

            # Register payload and emit only a reference key to avoid LLM context overflow
            data_key = register_data(json_str)

            # Log year span if available
            years = [r.get("anio") for r in json_rows if isinstance(r, dict) and isinstance(r.get("anio"), int)]
            if years:
                logger.info(f"Genie monthly JSON years: {min(years)}–{max(years)} ({len(set(years))} years, {len(json_rows)} rows)")

            # Build a compact markdown preview of the table used for analysis (first N rows)
            try:
                # No limits - show all data for complete analysis
                preview_md = self._rows_to_markdown(json_rows)  # Process all rows
                preview_count = len(json_rows)
            except Exception:
                preview_md = None
                preview_count = 0

            # Compose enhanced content including key, optional SQL, and a table preview
            parts = [
                f"DATA_JSON_KEY:\n{data_key}",
            ]
            if sql_query:
                parts.append("SQL EJECUTADO:")
                parts.append(f"```sql\n{sql_query}\n```")
            if preview_md:
                table_description = f"TABLA ({preview_count} filas del dataset usado para el análisis):"
                if preview_count == len(json_rows):
                    table_description = f"TABLA (dataset completo - {preview_count} filas):"
                else:
                    table_description = f"TABLA (primeras {preview_count} filas del dataset - total: {len(json_rows)} filas):"
                parts.append(table_description)
                parts.append(preview_md)
            parts.append(f"**Fuente de datos consultada:** {self.data_source_reference}")
            enhanced_content = "\n\n".join(parts)

            enhanced_message = AIMessage(content=enhanced_content, name="text_sql")
            enhanced_messages = messages[:-1] + [enhanced_message]
            updated_result = {**result, "messages": enhanced_messages}
            # Pass both forms in state for downstream robustness
            updated_result["tabular_data"] = extracted_tables
            updated_result["tabular_json"] = json_str
            # Also include the key as structured field for deterministic consumption downstream
            updated_result["data_ref_key"] = data_key
            # Include SQL for downstream/UX usage if available
            if sql_query:
                updated_result["sql_query"] = sql_query
            return updated_result
        else:
            # No table detected: do NOT add the source reference; forward original content
            enhanced_message = AIMessage(content=original_content, name="text_sql")
            enhanced_messages = messages[:-1] + [enhanced_message]
            updated_result = {**result, "messages": enhanced_messages}
            return updated_result

    
    def _extract_tabular_data(self, content: str) -> list[Dict[str, str]]:
        """
        Extract tabular data from markdown tables in the content.
        Robust to alignment rows (---, :---:), and lets the parser drop index columns.
        """
        tables: list[Dict[str, str]] = []
        lines = content.split('\n')
        table_lines: list[str] = []
        in_table = False
        # Alignment row pattern: |---:|:---|---|
        alignment_re = re.compile(r'^\s*\|(?:\s*:?-+:?\s*\|)+\s*$')

        for line in lines:
            stripped = line.strip()
            if stripped.startswith('|') and stripped.endswith('|') and stripped.count('|') >= 2:
                # Skip alignment rows entirely
                if alignment_re.match(stripped):
                    in_table = True
                    continue
                table_lines.append(stripped)
                in_table = True
            else:
                if in_table and table_lines:
                    # End current table block
                    table_data = self._parse_markdown_table(table_lines)
                    if table_data:
                        tables.extend(table_data)
                    table_lines = []
                    in_table = False
        # Process trailing table
        if in_table and table_lines:
            table_data = self._parse_markdown_table(table_lines)
            if table_data:
                tables.extend(table_data)
        return tables
    
    def _extract_sql_query(self, content: str) -> str | None:
        """Try to extract the SQL query from a code block or plain text."""
        try:
            # Prefer fenced code block ```sql ... ```
            m = re.search(r"```sql\s*\n([\s\S]*?)```", content, flags=re.IGNORECASE)
            if m:
                return m.group(1).strip()
            # Fallback: any fenced code block containing SELECT
            m = re.search(r"```[a-zA-Z]*\s*\n([\s\S]*?\bSELECT\b[\s\S]*?)```", content, flags=re.IGNORECASE)
            if m:
                return m.group(1).strip()
            # Fallback: inline SELECT ... ; capture until line with semicolon or end
            m = re.search(r"\bSELECT\b[\s\S]*?(?:;|$)", content, flags=re.IGNORECASE)
            if m:
                return m.group(0).strip()
        except Exception:
            return None
        return None
    
    def _rows_to_markdown(self, rows: list[Dict[str, Any]], max_rows: int = None) -> str:
        """Render a list of dict rows into a Markdown table (first max_rows)."""
        if not rows:
            return ""
        # Determine columns from union of keys preserving common order
        cols: list[str] = []
        seen = set()
        for r in rows:
            if not isinstance(r, dict):
                continue
            for k in r.keys():
                if k not in seen:
                    seen.add(k)
                    cols.append(str(k))
        if not cols:
            return ""
        # Build header and separator
        header = "| " + " | ".join(cols) + " |"
        separator = "| " + " | ".join(["---" for _ in cols]) + " |"
        lines = [header, separator]
        # Add all rows - no limits for Polars processing
        rows_to_process = rows if max_rows is None else rows[:max_rows]
        for r in rows_to_process:
            vals = []
            for c in cols:
                v = r.get(c, "")
                if isinstance(v, float):
                    # compact formatting while preserving decimals
                    v = ("{:.6g}".format(v))
                vals.append(str(v))
            lines.append("| " + " | ".join(vals) + " |")
        return "\n".join(lines)
    
    def _parse_markdown_table(self, table_lines: list[str]) -> list[Dict[str, str]]:
        """
        Parse a list of markdown table lines into a list of dictionaries.
        Skips alignment rows and PRESERVES all columns exactly as in the markdown (no dropping).
        """
        if not table_lines:
            return []
        try:
            alignment_re = re.compile(r'^\s*\|(?:\s*:?-+:?\s*\|)+\s*$')
            # Find header line (first non-alignment)
            header_idx = None
            for i, ln in enumerate(table_lines):
                if not alignment_re.match(ln.strip()):
                    header_idx = i
                    break
            if header_idx is None:
                return []
            header_line = table_lines[header_idx]
            header_cells = [c.strip() for c in header_line.strip('|').split('|')]
            if not header_cells:
                return []
            # Do NOT drop the leftmost header; preserve index-like columns as-is
            # Fallback names if all headers are empty
            if not any(header_cells):
                header_cells = [f"col_{i}" for i in range(len(header_cells))]

            def cast_val(s: str):
                s = s.strip()
                if s == "":
                    return None
                # int
                if re.fullmatch(r'-?\d+', s):
                    try:
                        return int(s)
                    except Exception:
                        return s
                # float incl scientific notation; allow thousands separator removal
                s2 = s.replace(',', '')
                if re.fullmatch(r'-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?', s2):
                    try:
                        return float(s2)
                    except Exception:
                        return s
                return s

            rows: list[Dict[str, str]] = []
            for ln in table_lines[header_idx + 1:]:
                s = ln.strip()
                if alignment_re.match(s):
                    continue
                if not (s.startswith('|') and s.endswith('|')):
                    continue
                cells = [c.strip() for c in s.strip('|').split('|')]
                # Align lengths
                if len(cells) < len(header_cells):
                    cells += [''] * (len(header_cells) - len(cells))
                elif len(cells) > len(header_cells):
                    cells = cells[:len(header_cells)]
                row = {k: cast_val(v) for k, v in zip(header_cells, cells)}
                # Skip row if all values empty/None
                if not any(v is not None and v != '' for v in row.values()):
                    continue
                rows.append(row)
            return rows
        except Exception as e:
            logger.error(f"Failed to parse markdown table: {e}")
            return []


    def _to_monthly_json(self, rows: list[Dict[str, str]]) -> list[Dict[str, str]]:
        """
        Faithful conversion: return the parsed markdown rows exactly as-is (no aggregation,
        no column renaming, no filtering), preserving the original row order.
        """
        if not rows:
            return []
        # Just return rows as parsed, preserving key order from the header and raw values
        logger.info("Text-to-SQL: Returning raw rows with no aggregation or manipulation (rows=%d)", len(rows))
        return rows

# Create the enhanced genie agent instance
genie_agent = GenieAgentWithReferences()
