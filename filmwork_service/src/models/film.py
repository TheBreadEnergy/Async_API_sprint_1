from typing import Optional
from uuid import UUID

from fastapi import Query

# Используем pydantic для упрощения при перегонке данных из json в объекты
from pydantic import BaseModel


class NameMixin(BaseModel):
    id: UUID
    name: str


class Person(NameMixin):
    pass


class Genre(NameMixin):
    pass


class Film(BaseModel):
    id: UUID
    title: str
    imdb_rating: Optional[float] | None
    description: Optional[str] | None = None
    genres: Optional[list[Genre]] = []
    actors: Optional[list[Person]] = []
    writers: Optional[list[Person]] = []
    director: Optional[list[str]] = []


class Films(Film):
    page: int = (Query(ge=0, default=0),)
    size: int = Query(ge=1, le=100, default=40)
