"""
Utils Package

Contains utility functions and helper modules used throughout the SoyBot system.
"""

# Import commonly used utilities
try:
    from .logger import logger
    from .session_manager import session_manager
    from .summarizer import *
    from .tavily import *
    
    __all__ = ["logger", "session_manager"]
except ImportError as e:
    # Some utility modules might have missing dependencies
    import warnings
    warnings.warn(f"Some utility modules could not be imported: {e}")
    __all__ = []
