from core.base_node import ConditionalNode
from agents.experto_estudios import market_study_agent


class MarketStudyNodeImpl(ConditionalNode):
    """
    Market study analysis node that uses a ConditionalNode:
    - success_route -> supervisor when RESPUESTA FINAL is present
    - continue_route -> market_study_agent to keep iterating when not final
    This mirrors a looping behavior using the shared ConditionalNode pattern used in sales.
    """

    def __init__(self):
        super().__init__(
            agent=market_study_agent,
            node_name="market_study_agent",
            success_route="supervisor",
            continue_route="market_study_agent",
            max_retries=3,
            fallback_response="RESPUESTA FINAL: He analizado los estudios pero necesito más detalles específicos para proporcionar una respuesta completa. Por favor, reformula tu consulta con más detalles específicos.",
        )

    def _get_agent_display_name(self) -> str:
        """Custom display name for logging"""
        return "Experto Estudios"


# Create the node instance - maintains the same function interface for existing code
market_study_node = MarketStudyNodeImpl()
