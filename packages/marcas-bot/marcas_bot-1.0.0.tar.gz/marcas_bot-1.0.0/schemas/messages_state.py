from langgraph.graph import MessagesState
from typing import Optional, Dict, List


class State(MessagesState):
    next: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    # Loop detection counters to prevent infinite loops
    node_retry_counts: Optional[Dict[str, int]] = None
    # Tabular data extracted from agents for advanced analysis
    tabular_data: Optional[List[Dict[str, str]]] = None
