from base import EntityMixinES
from movie_es import FilmParticipantES
from typing import Optional, List


class PersonFilmworkRoleES(EntityMixinES):
    title: str
    role: str


class PersonES(FilmParticipantES):
    name: str
    gender: str
    film_roles: Optional[List[PersonFilmworkRoleES]] = []
