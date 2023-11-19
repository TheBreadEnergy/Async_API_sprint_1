from uuid import UUID

from fastapi import Query
from pydantic import BaseModel
from src.models.genre import Genre
from src.models.person import Person


class Film(BaseModel):
    id: UUID
    title: str
    imdb_rating: float | None
    description: str | None = None
    genres: list[Genre] | None = []
    actors: list[Person] | None = []
    writers: list[Person] | None = []
    director: list[str] | None = []


class Films(Film):
    page: int = Query(ge=0, default=0)
    size: int = Query(ge=1, le=100, default=40)
