"""
Lazy Loading Utilities for Heavy Data Science Libraries

Only imports polars, numpy, scipy, and pandas when actually needed.
Saves ~150MB of RAM on startup if analytics aren't used immediately.

Memory impact per library:
- Polars: ~28MB
- Numpy: ~20MB  
- Scipy: ~48MB
- Pandas: ~55MB
- TOTAL: ~150MB
"""

from typing import Any
from utils.logger import logger

# Global cache for loaded modules
_polars = None
_numpy = None
_scipy_stats = None
_pandas = None

def get_polars():
    """
    Lazy import polars - only loads when data processing is needed
    Saves ~28MB of RAM if polars isn't used
    """
    global _polars
    if _polars is None:
        try:
            logger.debug("Lazy loading polars...")
            import polars as pl
            _polars = pl
            logger.info("Successfully loaded polars")
        except ImportError as e:
            logger.error(f"Failed to import polars: {e}")
            raise ImportError(f"polars is required for data processing: {e}")
    return _polars

def get_numpy():
    """
    Lazy import numpy - only loads when numerical computations are needed
    Saves ~20MB of RAM if numpy isn't used
    """
    global _numpy
    if _numpy is None:
        try:
            logger.debug("Lazy loading numpy...")
            import numpy as np
            _numpy = np
            logger.info("Successfully loaded numpy")
        except ImportError as e:
            logger.error(f"Failed to import numpy: {e}")
            raise ImportError(f"numpy is required for numerical analysis: {e}")
    return _numpy

def get_scipy_stats():
    """
    Lazy import scipy.stats - only loads when statistical tests are needed
    Saves ~48MB of RAM if statistical tests aren't used
    """
    global _scipy_stats
    if _scipy_stats is None:
        try:
            logger.debug("Lazy loading scipy.stats...")
            from scipy import stats
            _scipy_stats = stats
            logger.info("Successfully loaded scipy.stats")
        except ImportError as e:
            logger.error(f"Failed to import scipy.stats: {e}")
            raise ImportError(f"scipy is required for statistical tests: {e}")
    return _scipy_stats

def get_pandas():
    """
    Lazy import pandas - only loads when pandas operations are needed
    Saves ~55MB of RAM if pandas isn't used
    """
    global _pandas
    if _pandas is None:
        try:
            logger.debug("Lazy loading pandas...")
            import pandas as pd
            _pandas = pd
            logger.info("Successfully loaded pandas")
        except ImportError as e:
            logger.error(f"Failed to import pandas: {e}")
            raise ImportError(f"pandas is required for data processing fallback: {e}")
    return _pandas

def is_loaded(library: str) -> bool:
    """Check if a library has been loaded yet"""
    if library == 'polars':
        return _polars is not None
    elif library == 'numpy':
        return _numpy is not None
    elif library == 'scipy':
        return _scipy_stats is not None
    elif library == 'pandas':
        return _pandas is not None
    else:
        return False

def get_memory_status():
    """Get current memory status for debugging"""
    return {
        'polars_loaded': _polars is not None,
        'numpy_loaded': _numpy is not None,
        'scipy_loaded': _scipy_stats is not None, 
        'pandas_loaded': _pandas is not None,
        'estimated_ram_saved': _calculate_ram_saved()
    }

def _calculate_ram_saved():
    """Estimate RAM saved by not loading libraries yet"""
    saved = 0
    if not _polars:
        saved += 28   # ~28MB for polars
    if not _numpy:
        saved += 20   # ~20MB for numpy
    if not _scipy_stats:
        saved += 48   # ~48MB for scipy
    if not _pandas:
        saved += 55   # ~55MB for pandas
    return f"~{saved}MB"

def preload_all():
    """Preload all libraries - useful for warming up in production"""
    logger.info("Preloading all data science libraries...")
    get_polars()
    get_numpy() 
    get_scipy_stats()
    get_pandas()
    logger.info("All libraries preloaded")
