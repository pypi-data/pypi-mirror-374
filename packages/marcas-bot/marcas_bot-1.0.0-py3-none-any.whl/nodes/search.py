from core.base_node import ConditionalNode
from agents.agente_web import search_agent


class SearchNodeImpl(ConditionalNode):
    """
    Web search node using the ConditionalNode pattern:
    - success_route -> supervisor when final
    - continue_route -> search_agent to iterate until final
    """
    
    def __init__(self):
        super().__init__(
            agent=search_agent,
            node_name="search_agent",
            success_route="supervisor",
            continue_route="search_agent",
            max_retries=3,
            fallback_route="supervisor",
            fallback_response="RESPUESTA FINAL: He realizado búsquedas web pero necesito más información específica para proporcionar una respuesta completa. Por favor, reformula tu consulta con más detalles."
        )
    
    def _get_agent_display_name(self) -> str:
        """Custom display name for logging"""
        return "Agente Web"
    
    def _is_final_response(self, response: str) -> bool:
        """Allow finalization if response has RESPUESTA FINAL and at least one URL anywhere in the text"""
        if "RESPUESTA FINAL" not in response:
            return False
        # Count URLs anywhere in the response (not just in references section)
        import re
        urls = re.findall(r"https?://[^\s)\]\"<>]+", response, flags=re.IGNORECASE)
        return len(set(urls)) >= 1


# Create the node instance - maintains the same function interface for existing code
search_node = SearchNodeImpl()
