"""
Agents Package

Contains legacy agent implementations. These are being replaced by the
more modular node-based architecture in the nodes/ package.
"""

# Import agent classes for backward compatibility
try:
    from .agente_web import *
    from .analista_ventas import *
    from .experto_estudios import *
    from .synthesizer import *
    from .text_sql import *
    
    __all__ = []  # Will be populated by individual modules using __all__
except ImportError:
    # Some agents might not be available depending on dependencies
    __all__ = []
