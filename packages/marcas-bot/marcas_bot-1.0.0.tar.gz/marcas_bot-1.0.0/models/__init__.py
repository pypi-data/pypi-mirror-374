"""
Models Package

Contains LLM model implementations and wrappers for different AI providers
used throughout the SoyBot system.
"""

# Import model classes
try:
    from .agentic_llm import *
    from .databricks_llm import *
    
    __all__ = []  # Will be populated by individual modules using __all__
except ImportError as e:
    # Model modules might have missing dependencies (API keys, libraries, etc.)
    import warnings
    warnings.warn(f"Some model modules could not be imported: {e}")
    __all__ = []
