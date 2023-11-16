from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from models.film import Genre, Person
from pydantic import BaseModel
from services.film import FilmService, get_film_service

router = APIRouter()


class MixinFilms(BaseModel):
    id: UUID
    title: str
    imdb_rating: float | None


class Film(MixinFilms):
    description: str | None
    genres: list[Genre]
    actors: list[Person]
    writers: list[Person]
    director: list[str]


class Films(MixinFilms):
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
    film_id: UUID, film_service: FilmService = Depends(get_film_service)
) -> Film:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")

    return film


# Add descriptions
# Add new method /search with the same query params
@router.get(
    "/search/",
    response_model=list[Films],
    description="Поиск подробной информации о кинопроизведениях",
    tags=["Фильмы"],
    summary="Поиск информации о кинопроизведениях",
    response_description="Информация о кинопроизведении",
)
async def search_films(
    id_film: UUID = None,
    title: str = None,
    film_service: FilmService = Depends(get_film_service),
    page: int = Query(ge=1, default=1),
    size: int = Query(ge=1, le=100, default=40),
) -> list[Films]:
    films = await film_service.search_film(id_film, title, page, size)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="films not found")
    print(films)
    return films


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
    id_film: UUID = None,
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
