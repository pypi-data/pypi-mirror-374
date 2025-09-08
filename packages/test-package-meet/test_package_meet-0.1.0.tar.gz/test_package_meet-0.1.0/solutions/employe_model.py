from typing import Optional

from pydantic import BaseModel, Field


class Employee(BaseModel):
    id: int
    name: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Employee Name",
        examples=["meet kumar"],
    )
    department: Optional[str] = "General"
    salary: float = Field(
        ...,
        ge=1_00_000.00,
        decimal_places=2,
        description="Employee Salary",
        examples=[50_000.00, 80_000.00, 1_00_000.00],
    )
