from typing import Optional

import orjson
from fastapi import Query

# Используем pydantic для упрощения при перегонке данных из json в объекты
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    # orjson.dumps возвращает bytes, а pydantic требует unicode, поэтому декорируем
    return orjson.dumps(v, default=default).decode()


class NameMixin(BaseModel):
    id: str
    name: str


class Person(NameMixin):
    pass


class Genre(NameMixin):
    pass


class Film(BaseModel):
    id: str
    title: str
    imdb_rating: Optional[float] = None
    description: Optional[str] = None
    genres: Optional[list[Genre]] = []
    actors: Optional[list[Person]] = []
    writers: Optional[list[Person]] = []
    director: Optional[list[str]] = []


class Films(Film):
    page: int = (Query(ge=0, default=0),)
    size: int = Query(ge=1, le=100, default=40)