from base import EntityMixinES
from typing import Optional, List


class FilmParticipantES(EntityMixinES):
    name: str


class MovieES(EntityMixinES):
    title: str
    imdb_rating: Optional[float] = None
    genre: Optional[List[str]] = None
    description: Optional[str] = None
    director: Optional[List[str]] = []
    actors_names: Optional[List[str]] = []
    writers_names: Optional[List[str]] = []
    actors: Optional[List[FilmParticipantES]] = []
    writers: Optional[List[FilmParticipantES]] = []
