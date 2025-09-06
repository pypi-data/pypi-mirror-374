"""
Tools Package

Contains utility tools and external service integrations used by the
SoyBot agents for vector search, web search, and other operations.
"""

# Import tool modules
try:
    from .filter_studies import *
    from .rag import *
    from .web_search import *

    __all__ = []  # Will be populated by individual modules using __all__
except ImportError as e:
    # Tool modules might have missing dependencies (API keys, external services)
    import warnings

    warnings.warn(f"Some tool modules could not be imported: {e}")
    __all__ = []
