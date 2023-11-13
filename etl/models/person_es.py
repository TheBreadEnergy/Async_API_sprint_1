from typing import List, Optional
from uuid import UUID

from models.base import EntityMixinES
from pydantic import BaseModel


class PersonFilmworkRoleES(BaseModel):
    film_id: UUID
    role: str


class PersonES(EntityMixinES):
    name: str
    gender: Optional[str] = ""
    film_roles: Optional[List[PersonFilmworkRoleES]] = []
