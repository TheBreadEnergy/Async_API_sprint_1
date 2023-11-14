from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query

from models.genre import Genre

from services.genres import GenreService, get_genre_service

router = APIRouter()


@router.get(
    "/{genre_id}",
    response_model=Genre,
    description="Вывод подробной информации о запрашиваемом жанре",
    tags=["Жанры"],
    summary="Подробная информация о жанре",
    response_description="Информация о жанре",
)
async def genre_details(
        genre_id: str, genre_service: GenreService = Depends(get_genre_service)
) -> Genre:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genre not found")

    return genre


@router.get(
    "/",
    response_model=list[Genre],
    description="Вывод подробной информации о запрашиваемых жанрах",
    tags=["Жанры"],
    summary="Подробная информация о жанрах",
    response_description="Информация о жанрах",
)
async def list_genres(
        sort: str = Query(default='asc', regex="^(asc|desc)$"),
        id_genre: str = None,
        page: int = Query(ge=1, default=1),
        size: int = Query(ge=1, le=100, default=40),
        genre_service: GenreService = Depends(get_genre_service),
) -> list[Genre]:
    data_filter = {}
    if id_genre:
        data_filter["id"] = id_genre
    genres = await genre_service.get_all(sort, data_filter, page, size)
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genres not found")
    return genres
