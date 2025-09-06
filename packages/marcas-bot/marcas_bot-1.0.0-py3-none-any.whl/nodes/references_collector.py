from core.base_node import SimpleNode
from agents.references_collector import ReferencesCollectorAgent


class ReferencesCollectorNodeImpl(SimpleNode):
    """Node to consolidate internal and external references before synthesis."""

    def __init__(self):
        super().__init__(
            agent=ReferencesCollectorAgent(),
            node_name="references_collector",
            target_route="supervisor",  # research team's internal supervisor
            max_retries=3,
            fallback_response=(
                "No se pudieron consolidar referencias. Si persiste, el sintetizador debe revisar manualmente mensajes previos para extraer .pptx y URLs."
            ),
            forward_all_messages=True,  # forward the consolidated refs message as-is
        )

    def _get_agent_display_name(self) -> str:
        return "Creador Referencias"


# Node instance
references_collector_node = ReferencesCollectorNodeImpl()
