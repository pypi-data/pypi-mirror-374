#!/usr/bin/env python
"""
Modular Market Study Agent using the Base Bot class

This script creates a market study-focused agent that can:
1. Analyze market research queries
2. Extract qualitative market data from studies conducted between 2004-2024
3. Provide synthesized market analysis

Usage:
    python -m main.market_study_bot "What are the trends in soy consumption?"
    python -m main.market_study_bot --interactive
"""

import sys

from core.base_bot import BaseBot
from nodes.market_study import market_study_node
from nodes.synthesizer import call_synthesizer
from nodes.references_collector import references_collector_node


class MarketStudyBot(BaseBot):
    """A modular market study agent focused on qualitative market research"""

    def __init__(self):
        """Initialize the market study agent"""
        # Set up bot-specific configuration
        self.name = "Agente de Estudios de Mercado"
        
        # Define team members for this agent
        self.members = {
            "market_study_agent": "Experto en estudios cualitativos de mercado realizados entre 2004-2024. Una vez que proporciona RESPUESTA FINAL con análisis y documentos citados, debe ser seguido por references_collector.",
            "references_collector": "Recolector de referencias que consolida documentos internos y URLs externos mencionados en las conversaciones. Usar después de obtener respuesta final del market_study_agent.",
            "synthesizer": "Agente con funcionalidad de crear una respuesta FINAL para el usuario dada la informacion recompilada. ÚNICAMENTE el synthesizer debe proporcionar respuestas finales. Utilizalo al final para formular un mensaje y despues llama FINISH.",
        }

        # Define the nodes for this agent (supervisor added automatically by BaseBot)
        self.nodes = {
            "market_study_agent": market_study_node,
            "references_collector": references_collector_node,
            "synthesizer": call_synthesizer,
        }
        
        # Initialize the base bot (handles all the common setup)
        super().__init__()
    
    def get_description(self) -> str:
        """Return description for CLI help"""
        return "This agent specializes in qualitative market research analysis. It can analyze market studies conducted between 2004-2024."


def main():
    """Main entry point"""
    agent = MarketStudyBot()
    return agent.main_cli()


if __name__ == "__main__":
    sys.exit(main())
