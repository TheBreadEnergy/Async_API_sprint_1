from typing import Optional


from pydantic import BaseModel


class Person(BaseModel):
    id: str
    name: str
