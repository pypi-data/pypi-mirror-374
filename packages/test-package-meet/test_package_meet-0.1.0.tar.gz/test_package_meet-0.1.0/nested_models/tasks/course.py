from typing import List

from pydantic import BaseModel


class Course(BaseModel):
    id: int
    name: str


class Module(BaseModel):
    id: int
    name: str
    description: str
    course: Course


class Lesson(BaseModel):
    id: int
    name: str
    description: str
    modules: List[Module]
