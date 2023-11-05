import orjson

# Используем pydantic для упрощения при перегонке данных из json в объекты
from pydantic import BaseModel
from typing import Optional


def orjson_dumps(v, *, default):
    # orjson.dumps возвращает bytes, а pydantic требует unicode, поэтому декорируем
    return orjson.dumps(v, default=default).decode()


class Person(BaseModel):
    id: str
    name: str


class Film(BaseModel):
    id: str
    title: str
    imdb_rating: Optional[float]
    description: Optional[str]
    genre: Optional[list[str]]
    actors: Optional[list[Person]]
    writers: Optional[list[Person]]
    director: Optional[str]

    class Config:
        # Заменяем стандартную работу с json нпа более быструю
        json_loads = orjson.loads
        json_dumps = orjson_dumps
