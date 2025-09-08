from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime


class User(BaseModel):
    id: int
    name: str
    is_active: bool


class Product(BaseModel):
    id: int
    name: str
    price: float
    in_stock: bool


class Cart(BaseModel):
    user_id: int
    items: List[Product]
    quantities: Dict[str, int]
    updated_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


input_data = {"id": 10, "name": "meet kumar", "is_active": True}

user = User(**input_data)
