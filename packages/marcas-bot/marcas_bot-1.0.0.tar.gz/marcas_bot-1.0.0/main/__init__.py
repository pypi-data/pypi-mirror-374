"""
Main Bot Implementations

Contains the different bot implementations that use the BaseBot class.
"""

# Import main bot classes for easier access
try:
    from .sales_bot import SalesBot
    from .market_study_bot import MarketStudyBot
    from .search_bot import SearchBot
    from .research_bot import ResearchBot

    __all__ = ["SalesBot", "MarketStudyBot", "SearchBot", "ResearchBot"]
except ImportError:
    # Some bots might not be available depending on dependencies
    __all__ = []
