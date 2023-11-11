from typing import List, Optional
from uuid import UUID

from models.base import EntityMixinES
from pydantic import BaseModel


class PersonFilmworkRoleES(BaseModel):
    film_id: Optional[UUID]
    role: Optional[str] = ""


class PersonES(EntityMixinES):
    name: str
    gender: str
    film_roles: Optional[List[PersonFilmworkRoleES]] = []
