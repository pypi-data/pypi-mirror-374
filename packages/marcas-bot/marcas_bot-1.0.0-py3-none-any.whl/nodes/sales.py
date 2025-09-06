from core.base_node import ConditionalNode
from agents.analista_ventas import sales_agent
import re
import json
from utils.logger import logger
from utils.data_registry import get_data as registry_get_data
from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage
from langgraph.types import Command


class SalesNodeImpl(ConditionalNode):
    """
    Sales analysis node that routes to supervisor when analysis is complete,
    or to text_sql to get more data when continuing.
    """

    def __init__(self):
        super().__init__(
            agent=sales_agent,
            node_name="sales_analyst",
            success_route="supervisor",
            continue_route="text_sql",
            max_retries=6,
            fallback_response="He intentado analizar los datos de ventas solicitados, pero he encontrado dificultades para obtener la información completa. Este análisis será procesado por el synthesizer.",
        )

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced call method that detects data_ref_key from recent messages and adds it to state.
        Also extracts and provides column information for intelligent grouping.
        Additionally, enforces a hard guard: if the LLM tries to finalize without
        any sales data key present, it will re-route to text_sql with a one-line
        data request to avoid hallucinated final answers.
        """
        # RETRIES
        retry_counts = state.get("node_retry_counts", {}).copy()
        current_retries = retry_counts.get(self.node_name, 0)
        if current_retries >= self.max_retries:
            return self._handle_max_retries_exceeded(retry_counts)

        # 1) Detect recently provided DATA_JSON_KEY from text_sql
        if not state.get("data_ref_key"):
            messages = state.get("messages", []) or []
            for m in reversed(messages[-5:]):
                try:
                    name = getattr(m, "name", None)
                    content = getattr(m, "content", "")
                except Exception:
                    name, content = None, ""
                if name == "text_sql" and isinstance(content, str) and "DATA_JSON_KEY" in content:
                    match = re.search(r"DATA_JSON_KEY:\s*[\r\n]+([^\r\n]+)", content)
                    if match:
                        candidate = match.group(1).strip()
                        if candidate.startswith("data:"):
                            state["data_ref_key"] = candidate
                            logger.info(f"SalesNode: Detected data_ref_key in state: {candidate}")
                            columns_info = self._extract_column_info(candidate)
                            if columns_info:
                                state["available_columns"] = columns_info
                                logger.info(f"SalesNode: Extracted column info: {columns_info}")
                            break

        # 2) Add system_info with available columns for the LLM
        try:
            data_ref_key = state.get("data_ref_key")
            available_columns = state.get("available_columns")
            if data_ref_key:
                system_content = f"[SYSTEM INFO] DATA_REF_KEY_AVAILABLE: {data_ref_key}"
                if available_columns:
                    system_content += "\n\n[AVAILABLE COLUMNS FOR ANALYSIS]"
                    system_content += f"\nTotal records: {available_columns.get('total_records', 'unknown')}"
                    system_content += "\n\nColumns with types and sample values:"
                    for col_name, col_info in available_columns.get("columns", {}).items():
                        col_type = col_info.get("type", "unknown")
                        sample_values = col_info.get("sample_values", [])
                        unique_count = col_info.get("unique_count", 0)
                        system_content += f"\n• {col_name} ({col_type}): {unique_count} unique values"
                        if sample_values:
                            if col_type == "numeric":
                                system_content += f" [examples: {', '.join(sample_values[:5])}]"
                            elif col_type == "categorical" and unique_count <= 10:
                                system_content += f" [all values: {', '.join(sample_values)}]"
                            else:
                                system_content += f" [examples: {', '.join(sample_values[:3])}]"
                    system_content += "\n\n[GROUPING SUGGESTIONS]"
                    good_grouping_cols = []
                    for col_name, col_info in available_columns.get("columns", {}).items():
                        col_type = col_info.get("type", "unknown")
                        unique_count = col_info.get("unique_count", 0)
                        if col_type == "categorical" and 2 <= unique_count <= 20:
                            good_grouping_cols.append(col_name)
                    if good_grouping_cols:
                        system_content += f"\nRecommended for group_by_columns: {', '.join(good_grouping_cols)}"
                    numeric_cols = [
                        col_name
                        for col_name, col_info in available_columns.get("columns", {}).items()
                        if col_info.get("type") == "numeric"
                    ]
                    if numeric_cols:
                        system_content += f"\nRecommended for target_columns: {', '.join(numeric_cols)}"
                sys_msg = HumanMessage(content=system_content, name="system_info")
                enhanced_state = state.copy()
                enhanced_state["messages"] = state.get("messages", []) + [sys_msg]
                state = enhanced_state
        except Exception as e:
            logger.warning(f"SalesNode: Failed to build system_info message: {e}")

        # 3) Invoke the sales agent
        try:
            invocation_state = self._preprocess_state(state)
            prev_messages = invocation_state.get("messages", [])
            prev_len = len(prev_messages) if prev_messages else 0
            result = self.agent.invoke(invocation_state)
            all_messages = result.get("messages", [])
            response = all_messages[-1].content if all_messages else ""
            additional_fields = {k: v for k, v in result.items() if k not in ["messages"]}
            logger.info(f"{self._get_agent_display_name()} (attempt {current_retries + 1}): {response[:200]}...")
            if additional_fields:
                logger.info(f"Additional fields from agent: {list(additional_fields.keys())}")
        except Exception as e:
            logger.error(f"Error invoking {self._get_agent_display_name()}: {e}")
            return self._handle_agent_error(retry_counts, str(e))

        # 4) Guard: block finalization without sales data
        has_data_key = bool(state.get("data_ref_key")) or self._detect_data_key_in_messages(all_messages[prev_len:])
        if ("RESPUESTA FINAL" in response) and not has_data_key:
            # Build one-line data request to drive text_sql
            one_liner = self._build_data_request(invocation_state)
            updated_retry_counts = self._increment_retry_count(retry_counts, current_retries)
            logger.info("SalesNode: Blocking final response without data; requesting dataset and routing to text_sql")
            return Command(
                update={
                    "messages": [HumanMessage(content=one_liner, name=self.node_name)],
                    "node_retry_counts": updated_retry_counts,
                },
                goto=self.continue_route,
            )

        # 5) Normal processing via base routing
        updated_retry_counts = self._increment_retry_count(retry_counts, current_retries)
        return self._process_response(response, updated_retry_counts, current_retries, additional_fields)

    def _detect_data_key_in_messages(self, messages: List[Any]) -> bool:
        """Return True if any message contains a DATA_JSON_KEY data:... marker or system info data key."""
        try:
            for m in reversed(messages or []):
                content = getattr(m, "content", "") or ""
                if "DATA_JSON_KEY" in content and re.search(r"\bdata:[A-Za-z0-9]+", content):
                    return True
                if "[SYSTEM INFO] DATA_REF_KEY_AVAILABLE:" in content:
                    return True
        except Exception:
            return False
        return False

    def _build_data_request(self, state: Dict[str, Any]) -> str:
        """Construct a concise one-line request for the minimal dataset needed."""
        # Prefer a broad, reusable request that works for positioning/trends contexts
        return (
            "Ventas totales en USD y kilos Delisoy últimos 6 años, agregadas por año, "
            "país y claseProducto."
        )

    def _extract_column_info(self, data_ref_key: str) -> Optional[Dict[str, Any]]:
        """
        Extract column information from the data referenced by the key.
        Returns a dictionary with column names, types, and sample values.
        """
        try:
            # Get the data from registry
            raw_data = registry_get_data(data_ref_key)
            if not raw_data:
                logger.warning(f"SalesNode: Could not retrieve data for key {data_ref_key}")
                return None
            
            # Parse JSON data
            json_data = self._extract_json_array(raw_data)
            if not json_data:
                logger.warning(f"SalesNode: Could not extract JSON array from data")
                return None
            
            parsed_data = json.loads(json_data)
            if not isinstance(parsed_data, list) or not parsed_data or not isinstance(parsed_data[0], dict):
                logger.warning(f"SalesNode: Data is not a list of dictionaries")
                return None
            
            # Extract column information
            first_record = parsed_data[0]
            column_info = {
                "total_records": len(parsed_data),
                "columns": {}
            }
            
            # Analyze each column
            for col_name, col_value in first_record.items():
                # Determine column type
                col_type = self._infer_column_type(col_value)
                
                # Get ALL unique values for accurate count, but only show sample for display
                all_unique_values = set()
                for record in parsed_data:  # Analyze all records for complete column information
                    if col_name in record and record[col_name] is not None:
                        all_unique_values.add(str(record[col_name]))
                
                # Sample up to 10 values for display purposes
                sample_values = sorted(list(all_unique_values))[:10]
                
                column_info["columns"][col_name] = {
                    "type": col_type,
                    "sample_values": sample_values,
                    "unique_count": len(all_unique_values)  # Now shows actual unique count, not just sample count
                }
            
            logger.debug(f"SalesNode: Column analysis complete for {len(column_info['columns'])} columns")
            return column_info
            
        except Exception as e:
            logger.error(f"SalesNode: Error extracting column info: {str(e)}")
            return None
    
    def _extract_json_array(self, text: str) -> Optional[str]:
        """Extract a JSON array substring from mixed text."""
        if not text:
            return None
        
        s = text.strip()
        
        # If enclosed in code fences, strip them
        if s.startswith("```") and s.endswith("```"):
            s = s.strip('`').strip()
            # If there's a language tag like ```json
            if '\n' in s:
                s = s.split('\n', 1)[1].strip()
        
        # If prefixed with DATA_JSON:
        if s.upper().startswith("DATA_JSON"):
            # split on first '[' after prefix
            idx = s.find('[')
            if idx != -1:
                s = s[idx:]
        
        # If string starts with a quoted array, e.g., "[ {...} ]"
        if (s.startswith('"[') and s.endswith(']"')) or (s.startswith("'[") and s.endswith("]'")):
            try:
                s = json.loads(s)
            except Exception:
                return None
        
        # Extract the outermost [ ... ]
        lb = s.find('[')
        rb = s.rfind(']')
        if lb != -1 and rb != -1 and rb > lb:
            candidate = s[lb:rb+1].strip()
            # quick sanity check
            if candidate.startswith('[') and candidate.endswith(']'):
                return candidate
        
        return None
    
    def _infer_column_type(self, value) -> str:
        """Infer the data type of a column value."""
        if value is None:
            return "unknown"
        elif isinstance(value, (int, float)):
            return "numeric"
        elif isinstance(value, str):
            # Check if it looks like a date
            if re.match(r'^\d{4}-\d{1,2}-\d{1,2}', value):
                return "date"
            # Check if it looks like a numeric string
            try:
                float(value)
                return "numeric"
            except ValueError:
                return "categorical"
        elif isinstance(value, bool):
            return "boolean"
        else:
            return "other"
    
    def _get_agent_display_name(self) -> str:
        """Custom display name for logging"""
        return "Analista de Ventas"


# Create the node instance - maintains the same function interface for existing code
sales_node = SalesNodeImpl()
