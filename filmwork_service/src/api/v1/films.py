from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from models.film import Genre, Person
from pydantic import BaseModel
from services.film import FilmService, get_film_service

router = APIRouter()


class Film(BaseModel):
    id: str
    title: str
    imdb_rating: Optional[float]
    description: Optional[str]
    genre: Optional[list[Genre]]
    actors: Optional[list[Person]]
    writers: Optional[list[Person]]
    director: Optional[list[str]]


class Films(Film):
    page: int = (Query(ge=0, default=0),)
    size: int = Query(ge=1, le=100, default=40)


@router.get(
    "/{film_id}",
    response_model=Film,
    description="Вывод подробной информации о запрашиваемом кинопроизведении",
    tags=["Фильмы"],
    summary="Подробная информация о кинопроизведении",
    response_description="Информация о кинопроизведении",
)
async def film_details(
    film_id: str, film_service: FilmService = Depends(get_film_service)
) -> Film:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")

    return film


@router.get(
    "/",
    response_model=list[Films],
    description="Вывод подробной информации о запрашиваемых кинопроизведениях",
    tags=["Фильмы"],
    summary="Подробная информация о кинопроизведениях",
    response_description="Информация о кинопроизведениях",
)
async def list_films(
    sort=None,
    id_film: str = None,
    genre: str = None,
    actor_id: str = None,
    writer_id: str = None,
    page: int = Query(ge=1, default=1),
    size: int = Query(ge=1, le=100, default=40),
    film_service: FilmService = Depends(get_film_service),
) -> list[Films]:
    data_filter = {}
    if id_film:
        data_filter["id"] = id_film
    if genre:
        data_filter["genre"] = genre
    if actor_id:
        data_filter["actors"] = actor_id
    if writer_id:
        data_filter["writers"] = writer_id

    films = await film_service.get_all(sort, data_filter, page, size)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="films not found")
    return films
