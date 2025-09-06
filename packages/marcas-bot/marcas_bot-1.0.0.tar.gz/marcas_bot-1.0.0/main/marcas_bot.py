"""
Modular Super Bot using the Base Bot class

This script creates a comprehensive agent that can:
1. Coordinate research teams for internal market studies (2004-2024) and external web research, and sales.
2. Synthesize information from multiple sources (internal studies + web data + sales data)
4. Extract references from specific difference data sources
3. Provide integrated responses combining historical market research and current market intelligence

Usage:
    python -m main.marcas_bot "What are the market trends and competitive landscape for Delisoy?"
    python -m main.marcas_bot --interactive
"""

import sys

from core.base_bot import BaseBot
from nodes.research_team import call_research_team
from nodes.sales import sales_node
from nodes.sell_in_genie import sell_in
from nodes.synthesizer import call_synthesizer
from nodes.references_collector import references_collector_node


class MarcasBot(BaseBot):
    """A comprehensive bot that coordinates research teams and synthesis"""

    def __init__(self):
        """Initialize the super bot"""
        # Set up bot-specific configuration
        self.name = "MarcasBot - Asistente CSSA"

        # Define team members for this agent
        self.members = {
            "research_team": "Equipo capaz de ejecutar investigaciones en estudios de mercado internos (2004-2024) y búsquedas web externas para análisis competitivo de Delisoy.",
            "synthesizer": "Agente con funcionalidad de crear una respuesta para el usuario dada la informacion recompilada. Utilizalo al final para formular un mensaje y despues llama FINISH.",
            "sales_analyst": (
                "Analista de ventas con capacidad de extraer datos de ventas desde el 2012 al dia presente (2025). Utilizalo para brindar cifras monetarias internas que reflejan el mercado, encuesta de ventas generales, etc...",
                "Por ejemplo, si se observa una caída en la participación de mercado en un estudio de mercado, el analista de ventas puede proporcionar datos de ventas que confirmen o refuten esta tendencia.",
            ),
            "references_collector": "Recolector de referencias que consolida fuentes de datos mencionados en las conversaciones. Usar justo antes de synthesizer.",
        }

        # Define the nodes for this agent (supervisor added automatically by BaseBot)
        self.nodes = {
            "research_team": call_research_team,
            "synthesizer": call_synthesizer,
            "sales_analyst": sales_node,
            "text_sql": sell_in,
            "references_collector": references_collector_node,
        }

        # Initialize the base bot (handles all the common setup)
        super().__init__()

    def get_description(self) -> str:
        """Return description for CLI help"""
        return "This bot coordinates comprehensive research combining and sales."


def main():
    """Main entry point"""
    agent = MarcasBot()
    return agent.main_cli()


if __name__ == "__main__":
    sys.exit(main())
