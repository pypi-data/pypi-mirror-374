from core.base_node import SimpleNode
from core.base_agent import Agent
from nodes.market_study import market_study_node
from nodes.search import search_node
from nodes.references_collector import references_collector_node
from langchain_openai import ChatOpenAI
from config.params import OPENAI_API_KEY
from schemas.messages_state import State
from typing import Literal, Dict
from pydantic import BaseModel
from langgraph.types import Command
from langgraph.graph import END
from utils.logger import logger


# Research team configuration
equipo_investigacion = {
    "market_study_agent": (
        "Experto en estudios de mercado históricos de Delisoy (2004-2024). Usa para contexto interno de Delisoy y competidores cuando sea relevante para la consulta. "
    ),
    "search_agent": (
        "Especialista en búsqueda web externa. Usa para encontrar datos recientes, precios específicos, documentos, enlaces web relevantes a la consulta, y generar contexto con información externa."
    ),
    "references_collector": (
        "Consolida referencias internas (.pptx/.pdf/.docx) y enlaces externos (URLs) detectados en los mensajes previos. Ejecuta SIEMPRE antes del sintetizador."
    ),
}


def make_research_supervisor(llm, members: Dict[str, str]):
    """Create a specialized supervisor for research team that better coordinates data sources"""
    options = ["FINISH"] + [m for m in members.keys()]
    formatted_descriptions = "\n".join(
        f"- {name}: {desc}" for name, desc in members.items()
    )

    system_prompt = (
        "Eres un supervisor especializado en investigación que coordina entre estudios internos y búsquedas externas:\n"
        f"{formatted_descriptions}\n\n"
        "ESTRATEGIA DE INVESTIGACIÓN COORDINADA:\n"
        "1. ANÁLISIS INICIAL: Identifica si la consulta requiere:\n"
        "   - Solo datos internos (estudios históricos Delisoy 2004-2024): usa market_study_agent\n"
        "   - Solo datos externos (tendencias actuales, competencia, precios): usa search_agent\n"
        "   - Ambos tipos de datos para análisis integral: coordina ambos agentes\n\n"
        "2. COORDINACIÓN INTELIGENTE:\n"
        "   - Para consultas sobre POSICIONAMIENTO, EQUITY DE MARCA, TENDENCIAS: necesitas AMBOS tipos de datos\n"
        "   - Comienza con market_study_agent para datos históricos Delisoy\n"
        "   - Si la respuesta menciona limitaciones o falta de datos externos, usa search_agent\n"
        "   - Si ya tienes datos completos de ambas fuentes, usa FINISH\n\n"
        "3. SEÑALES PARA CONTINUAR INVESTIGACIÓN:\n"
        "   - 'información limitada', 'datos insuficientes', 'contexto externo'\n"
        "   - 'competencia actual', 'tendencias recientes', 'datos actualizados'\n"
        "   - Solo un tipo de dato disponible cuando se necesitan ambos\n\n"
        "4. USAR FINISH SOLO CUANDO:\n"
        "   - Tienes datos completos de todas las fuentes necesarias\n"
        "   - La consulta está completamente respondida\n"
        "   - No se requiere información adicional externa o interna\n\n"
        "IMPORTANTE: Para consultas sobre estrategia de marca, posicionamiento o análisis competitivo, SIEMPRE coordina ambos agentes para respuesta integral."
    )

    class Router(BaseModel):
        """Worker to route to next. If research complete, route to FINISH."""

        next: Literal[*options]

    def _needs_external(user_text: str) -> bool:
        # Keywords indicating need for current/external data
        kws = [
            "hoy",
            "actual",
            "actuales",
            "reciente",
            "recientes",
            "tendencia",
            "tendencias",
            "competencia",
            "competitivo",
            "precios",
            "noticias",
            "lanzamientos",
            "mercado actual",
        ]
        user_text = (user_text or "").lower()
        return any(k in user_text for k in kws)

    def _requires_both(user_text: str) -> bool:
        # Topics that by design require both internal studies and current external context
        kws = [
            "posicionamiento",
            "posicionamiento de marca",
            "equity",
            "equity de marca",
            "beneficios percibidos",
            "percepción",
            "brand equity",
        ]
        user_text = (user_text or "").lower()
        return any(k in user_text for k in kws)

    def _has_agent_message(messages, agent_name: str) -> bool:
        for m in messages:
            name = getattr(m, "name", None)
            if name == agent_name:
                return True
        return False

    def _has_links(messages) -> bool:
        """
        Detect if there are external links in the CURRENT TURN only.
        Important: The session manager injects a first HumanMessage with
        'CONTEXTO PREVIO' that can contain URLs from prior answers. We must
        ignore that to avoid falsely assuming external data is already present.
        """
        if not messages:
            return False
        # Consider only messages produced after the first (user) message
        current_turn = messages[1:]
        for m in current_turn:
            # Prefer to only consider AI messages (agents' outputs)
            mtype = getattr(m, "type", None)
            if mtype and str(mtype).lower() != "ai":
                continue
            content = getattr(m, "content", "")
            if isinstance(content, str) and (
                "http://" in content or "https://" in content
            ):
                return True
        return False

    def _has_collector(messages) -> bool:
        for m in messages:
            name = getattr(m, "name", None)
            if name == "references_collector":
                return True
        return False

    def research_supervisor_node(state: State) -> Command[Literal[*members, "__end__"]]:
        """Specialized research supervisor with hybrid rule-based + LLM coordination"""
        # Extract last user text and agent usage from current state
        user_text = ""
        for m in reversed(state["messages"]):
            # HumanMessage instances have no 'role' but have .name; we check type by absence of name equals 'user' usage
            if getattr(m, "type", None) == "human" or getattr(m, "name", None) not in (
                "market_study_agent",
                "search_agent",
                "research_team",
                "synthesizer",
            ):
                user_text = getattr(m, "content", "") or ""
                break

        messages = state["messages"]
        has_internal = _has_agent_message(messages, "market_study_agent")
        has_external = _has_agent_message(messages, "search_agent") or _has_links(
            messages
        )
        needs_external = _needs_external(user_text)
        requires_both = _requires_both(user_text)
        has_refs_collector = _has_collector(messages)

        # Rule-based guardrails
        if not has_internal:
            logger.info(
                "Research Supervisor (rules): routing to market_study_agent first"
            )
            return Command(
                goto="market_study_agent", update={"next": "market_study_agent"}
            )

        if (needs_external or requires_both) and not has_external:
            logger.info(
                "Research Supervisor (rules): external data needed -> routing to search_agent"
            )
            return Command(goto="search_agent", update={"next": "search_agent"})

        # If both internal and external present but consolidated refs not created yet -> create them
        if (has_internal and has_external) and not has_refs_collector:
            logger.info(
                "Research Supervisor (rules): creating consolidated references -> references_collector"
            )
            return Command(
                goto="references_collector", update={"next": "references_collector"}
            )

        # Fall back to LLM router when rules don't force a path
        messages_with_system = [{"role": "system", "content": system_prompt}] + messages
        response = llm.with_structured_output(Router).invoke(messages_with_system)
        goto = response.next
        logger.info(f"Research Supervisor (LLM): {goto}")

        # Prevent premature FINISH if both sources not covered and external is needed
        if goto == "FINISH":
            # Block FINISH if either needs_external or requires_both indicate external is needed
            if (needs_external or requires_both) and not has_external:
                logger.info(
                    "Research Supervisor override: FINISH blocked -> search_agent"
                )
                return Command(goto="search_agent", update={"next": "search_agent"})
            # Also block FINISH if requires_both and internal not yet present (edge case)
            if requires_both and not has_internal:
                logger.info(
                    "Research Supervisor override: FINISH blocked -> market_study_agent"
                )
                return Command(
                    goto="market_study_agent", update={"next": "market_study_agent"}
                )
            return Command(goto=END, update={"next": "FINISH"})

        return Command(goto=goto, update={"next": goto})

    return research_supervisor_node


# Create internal supervisor for the research team with improved coordination
supervisor = make_research_supervisor(
    ChatOpenAI(
        model="gpt-4o-mini",
        api_key=OPENAI_API_KEY,
        temperature=0.1,
        top_p=0.95,
    ),
    equipo_investigacion,
)

# Internal research team nodes
nodes = {
    "supervisor": supervisor,
    "market_study_agent": market_study_node,
    "search_agent": search_node,
    "references_collector": references_collector_node,
}

# Create the composite research team agent
research_team = Agent(State, nodes)


class ResearchTeamNodeImpl(SimpleNode):
    """
    Research team node that wraps a composite Agent containing market study and search agents.
    This is a SimpleNode that always routes to supervisor after completing internal research.
    """

    def __init__(self):
        super().__init__(
            agent=research_team,
            node_name="research_team",
            target_route="supervisor",
            max_retries=5,  # Research team needs more coordination attempts
            fallback_response="El equipo de investigación ha analizado los datos, pero no pudo completar la tarea. Por favor, brinda una encuesta más específica.",
            forward_all_messages=True,  # Only forward final response to prevent memory bloat
        )

    def _get_agent_display_name(self) -> str:
        """Custom display name for logging"""
        return "Supervisor Investigacion"


# Create the node instance - maintains the same function interface for existing code
call_research_team = ResearchTeamNodeImpl()
