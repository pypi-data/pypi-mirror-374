"""
Input schema for Polars data analysis tool
"""

from typing import Optional
from langchain_core.pydantic_v1 import BaseModel, Field


class PolarsAnalysisInput(BaseModel):
    """Input schema for Polars data analysis tool"""
    
    raw_data: str = Field(
        default="",
        description="Tabular data in markdown, CSV, or JSON format (leave empty if using data_ref)"
    )
    
    data_ref: Optional[str] = Field(
        default=None,
        description="Registry key referencing a preloaded tabular payload to avoid large tool arguments"
    )
    
    analysis_type: str = Field(
        default="descriptive",
        description="Type of analysis: descriptive, comparative, temporal, correlation, distribution, ranking, outlier, regression"
    )
    
    target_columns: Optional[str] = Field(
        None,
        description="Comma-separated list of columns to analyze"
    )
    
    group_by_columns: Optional[str] = Field(
        None,
        description="Comma-separated list of columns to group by"
    )
    
    time_column: Optional[str] = Field(
        None,
        description="Column name to use for temporal analysis"
    )
    
    aggregation_method: str = Field(
        default="sum",
        description="Method for aggregating data: sum, mean, median, count, min, max, std, var"
    )
    
    percentiles: str = Field(
        default="0.25,0.5,0.75",
        description="Comma-separated percentiles to calculate (e.g., '0.1,0.25,0.5,0.75,0.9')"
    )
    
    window_size: int = Field(
        default=3,
        description="Window size for rolling calculations"
    )
    
    correlation_threshold: float = Field(
        default=0.3,
        description="Minimum correlation strength to report (0.0-1.0)"
    )
    
    outlier_method: str = Field(
        default="iqr",
        description="Method for outlier detection: iqr or zscore"
    )
    
    outlier_threshold: float = Field(
        default=1.5,
        description="Threshold for outlier detection (1.5 for IQR, 2-3 for zscore)"
    )
    
    trend_periods: int = Field(
        default=5,
        description="Number of recent periods to analyze for trends"
    )
    
    statistical_tests: bool = Field(
        default=False,
        description="Whether to perform statistical significance tests"
    )
    
    confidence_level: float = Field(
        default=0.95,
        description="Confidence level for statistical tests (0.90, 0.95, 0.99)"
    )
    
    top_n: int = Field(
        default=10,
        description="Number of top/bottom items to show in rankings"
    )
