from core.base_engine import BaseEngine
from main.marcas_bot import MarcasBot
from utils.logger import logger


class MarcasBotEngine(BaseEngine):
    """
    Engine wrapper for the MarcasBot (super multi-agent bot combining sales, research, and synthesis).
    This provides a thin API layer around the modular MarcasBot implementation.
    """

    def __init__(self):
        """Initialize the MarcasBot engine."""
        super().__init__("marcas")
        # Backward compatibility attribute expected by some endpoints
        self.bot_runner = self.bot

    def _initialize_bot(self):
        """Initialize the MarcasBot instance"""
        try:
            self.bot = MarcasBot()
        except Exception as e:
            logger.error(f"Failed to initialize MarcasBot: {e}")
            raise


# Create a singleton instance and provide a compatible alias
marcas_engine = MarcasBotEngine()
