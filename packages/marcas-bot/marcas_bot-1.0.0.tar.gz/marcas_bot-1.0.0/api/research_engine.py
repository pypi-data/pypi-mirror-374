from core.base_engine import BaseEngine
from main.research_bot import ResearchBot
from utils.logger import logger


class ResearchBotEngine(BaseEngine):
    """
    Super engine that manages the comprehensive MarcasBot (ResearchBot) instances.
    This acts as a wrapper around the ResearchBot to provide API-specific functionality.
    """

    def __init__(self):
        """Initialize the MarcasBot engine."""
        super().__init__("super")
        # Keep the legacy attribute for backward compatibility
        self.bot_runner = self.bot

    def _initialize_bot(self):
        """Initialize the ResearchBot instance"""
        try:
            self.bot = ResearchBot()
        except Exception as e:
            logger.error(f"Failed to initialize ResearchBot: {e}")
            raise


# Create a singleton instance
research_engine = ResearchBotEngine()
