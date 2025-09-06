from pydantic import BaseModel, Field
from typing import Optional, List


class ChunkedRagInput(BaseModel):
    query_text: str = Field(description="Text query for semantic similarity search")
    doc_ids: Optional[List[str]] = Field(
        default=None,
        description="List of doc_id values to search within (from filter_summaries_sql results). If not provided, searches all documents.",  # Updated description
    )
    num_results: int = Field(
        default=80,
        ge=40,
        le=300,
        description="Number of results to return (max 300)",
    )
