from pydantic import BaseModel, Field, model_validator
from typing import Optional, List

ALLOWED_COUNTRIES = {"NICARAGUA", "INTERNACIONAL"}


class StudiesFilterInput(BaseModel):
    """
    Input schema for filtering the silver.external_data.<TABLE> by year (from file_path) and/or country.
    """

    year: Optional[int] = Field(
        default=None, description="Single year to filter by (from file_path)"
    )
    year_range: Optional[List[int]] = Field(  # Changed from Tuple to List
        default=None,
        description="Inclusive [start, end] year range as a list",
        min_length=2,
        max_length=2,
    )
    countries: Optional[List[str]] = Field(
        default=None, description='Allowed values: "Nicaragua", "Internacional"'
    )
    limit: int = Field(
        default=100, ge=1, description="Max rows to return (default 100, max 1000)"
    )

    @model_validator(mode="after")
    def _validate_any_filter(self):
        if self.year is None and self.year_range is None and not self.countries:
            raise ValueError(
                "Provide at least one filter: year, year_range, or countries"
            )
        if self.year_range is not None and len(self.year_range) != 2:
            raise ValueError("year_range must contain exactly 2 integers: [start, end]")
        if self.countries:
            norm = []
            for c in self.countries:
                if not c:
                    continue
                uc = str(c).strip().upper()
                if uc not in ALLOWED_COUNTRIES:
                    raise ValueError(
                        f"Invalid country '{c}'. Allowed: Nicaragua, Internacional"
                    )
                norm.append("Nicaragua" if uc == "NICARAGUA" else "Internacional")
            self.countries = norm
        return self
