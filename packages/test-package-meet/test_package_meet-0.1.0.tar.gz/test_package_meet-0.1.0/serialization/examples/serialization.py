from typing import Dict, List

from pydantic import BaseModel


class Property(BaseModel):
    id: int
    name: str
    dimension: Dict[str, float] = None
    total_square_feet: float = None
    rate_per_square_feet: float = None
    is_sold: bool = False


class Owner(BaseModel):
    id: int
    name: str
    properties: List[Property]


bhopal = Property(
    id=1,
    name="bhopal",
    dimension={"length": 100, "width": 100, "height": 100},
    total_square_feet=2.0,
    rate_per_square_feet=1.0,
)

indore = Property(
    id=2,
    name="indore",
    dimension={"length": 100, "width": 100, "height": 100},
    total_square_feet=2.0,
    rate_per_square_feet=1.0,
)

meet = Owner(id=3, name="mee", properties=[bhopal, indore])
