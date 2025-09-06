"""
Schemas Package

Contains data structures, Pydantic models, and type definitions
used for API requests, state management, and data validation.
"""

# Import schema classes
try:
    from .api_query_request import QueryRequest
    from .messages_state import State
    from .filter_studies_input import StudiesFilterInput
    from .polars_analysis_input import PolarsAnalysisInput
    from .rag_input import ChunkedRagInput

    __all__ = [
        "QueryRequest",
        "State",
        "StudiesFilterInput",
        "ChunkedRagInput",
        "PolarsAnalysisInput",
    ]
except ImportError as e:
    # Schema modules might have missing dependencies
    import warnings

    warnings.warn(f"Some schema modules could not be imported: {e}")
    __all__ = []
