from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from models.film import Person

from services.film import FilmService, get_film_service

# Объект router, в котором регистрируем обработчики
router = APIRouter()


# Модель ответа API
class Film(BaseModel):
    id: str
    title: str
    imdb_rating: Optional[float]
    description: Optional[str]
    genre: Optional[list[str]]
    actors: Optional[list[Person]]
    writers: Optional[list[Person]]
    director: Optional[str]


# Внедряем FilmService с помощью Depends(get_film_service)
@router.get(
    '/{film_id}',
    response_model=Film,
    description='Вывод всей информации о запрашиваемом кинопроизведении',
    tags=['Фильмы'],
    summary='Подробная информация о кинопроизведении',
    response_description='Информация о кинопроизведении'
)
async def film_details(
        film_id: str,
        film_service: FilmService = Depends(get_film_service)
) -> Film:
    film = await film_service.get_by_id(film_id)
    if not film:
        # Если фильм не найден, отдаем 404 статус
        # Желательно пользоваться уже определенными HTTP-статусами, которые содержат enum
        # такой код будет более поддерживаемым
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='film not found'
        )

    # Перекладываем данные из models.Film в Film
    # Обратите внимание, что у модели бизнес-логики есть поле description
    # Которое отсутствует в модели ответа API
    # Если бы использовалась общая модель для бизнес-логики и формирования ответов API
    # Вы бы предоставляли клиентам данные, которые им не нужны
    # и, возможно, данные, которые опасно возвращать
    return Film(
        id=film.id,
        title=film.title,
        imdb_rating=film.imdb_rating,
        description=film.description,
        genre=film.genre,
        actors=film.actors,
        writers=film.writers,
        director=film.director,
    )
