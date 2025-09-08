from typing import Optional, List

from pydantic import BaseModel


class Address(BaseModel):
    street: str
    city: str
    state: str


class Delivery(BaseModel):
    id: int
    address: Address


class Comment(BaseModel):
    id: int
    text: str
    replies: Optional[List["Comment"]] = None


##forward referencing
Comment.model_rebuild()
address = Address(street="shyamla hills", city="bhopal", state="madhya pradesh")

delivery = Delivery(id=1, address=address)

comment = Comment(
    id=1,
    text="hello world",
    replies=[Comment(id=2, text="hello world"), Comment(id=3, text="hello world")],
)
