from typing import List, Optional

from models.base import EntityMixinES
from models.movie_es import FilmParticipantES


class PersonFilmworkRoleES(EntityMixinES):
    title: str
    role: str


class PersonES(FilmParticipantES):
    name: str
    gender: str
    film_roles: Optional[List[PersonFilmworkRoleES]] = []
