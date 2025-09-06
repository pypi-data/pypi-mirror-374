"""
Configuration Package

Contains application configuration parameters and prompt templates
for the SoyBot system.
"""

# Import configuration modules
try:
    from .params import *
    from .prompts import *
    
    __all__ = []  # Will be populated by individual modules using __all__
except ImportError as e:
    # Configuration files might have missing dependencies
    import warnings
    warnings.warn(f"Some configuration modules could not be imported: {e}")
    __all__ = []
