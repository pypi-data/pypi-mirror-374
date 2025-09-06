#!/usr/bin/env python
"""
Modular Sales Agent using the Base Bot class

This script creates a sales-focused agent that can:
1. Analyze sales queries
2. Extract data from SQL databases via genie agent
3. Provide final sales analysis

Usage:
    python -m main.sales_bot "What were the sales figures for 2023?"
    python -m main.sales_bot --interactive
"""

import sys

from core.base_bot import BaseBot
from nodes.sales import sales_node
from nodes.sell_in_genie import sell_in
from nodes.synthesizer import call_synthesizer
from nodes.references_collector import references_collector_node


class SalesBot(BaseBot):
    """A modular sales agent focused on sales data analysis"""

    def __init__(self):
        """Initialize the sales agent"""
        # Set up bot-specific configuration
        self.name = "Agente de Ventas"

        # Define team members for this agent
        self.members = {
            "sales_analyst": "Analista de ventas, capaz de extraer datos de ventas y ejecutar analitica avanzada. NO debe dar respuestas finales, solo proporciona análisis que necesita ser procesado por el synthesizer.",
            "references_collector": "Recolector de referencias que consolida documentos internos y URLs externos mencionados en las conversaciones. Usar después de obtener datos del sales_analyst.",
            "synthesizer": "Agente con funcionalidad de crear una respuesta FINAL para el usuario dada la informacion recompilada. ÚNICAMENTE el synthesizer debe proporcionar respuestas finales. Utilizalo al final para formular un mensaje y despues llama FINISH.",
        }

        # Define the nodes for this agent (supervisor added automatically by BaseBot)
        self.nodes = {
            "sales_analyst": sales_node,
            "text_sql": sell_in,
            "references_collector": references_collector_node,
            "synthesizer": call_synthesizer,
        }

        # Initialize the base bot (handles all the common setup)
        super().__init__()

    def get_description(self) -> str:
        """Return description for CLI help"""
        return "This agent specializes in sales data analysis and queries. It can extract and analyze sales data from your database."


def main():
    """Main entry point"""
    agent = SalesBot()
    return agent.main_cli()


if __name__ == "__main__":
    sys.exit(main())
