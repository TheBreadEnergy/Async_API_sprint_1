from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query

from models.person import Person

from services.persons import PersonService, get_person_service

router = APIRouter()


@router.get(
    "/{person_id}",
    response_model=Person,
    description="Вывод подробной информации о запрашиваемом персоне",
    tags=["Персоны"],
    summary="Подробная информация о персоне",
    response_description="Информация о персоне",
)
async def person_details(
        person_id: str, person_service: PersonService = Depends(get_person_service)
) -> Person:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")

    return person


@router.get(
    "/",
    response_model=list[Person],
    description="Вывод подробной информации о запрашиваемых персонах",
    tags=["Персоны"],
    summary="Подробная информация о персонах",
    response_description="Информация о персонах",
)
async def list_persons(
        sort: str = Query(default='asc', regex="^(asc|desc)$"),
        id_person: str = None,
        page: int = Query(ge=1, default=1),
        size: int = Query(ge=1, le=100, default=40),
        person_service: PersonService = Depends(get_person_service),
) -> list[Person]:
    data_filter = {}
    if id_person:
        data_filter["id"] = id_person
    persons = await person_service.get_all(sort, data_filter, page, size)
    if not persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="persons not found")
    return persons
