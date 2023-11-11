import logging

from queries.base import BaseQuery
from queries.settings import MOVIE_TABLE, PERSON_MOVIE_TABLE, PERSON_TABLE

logger = logging.getLogger(__name__)


class PersonQuery(BaseQuery):
    _query = f"""
    SELECT person.id, person.full_name AS name, person.gender AS gender,
    ARRAY_AGG(
    DISTINCT jsonb_build_object('id', film.id, 'title', film.title, 'role', person_film.role)) AS film_roles,
    person.modified AS modified
    FROM {PERSON_TABLE} person
    LEFT JOIN {PERSON_MOVIE_TABLE} AS person_film ON person_film.person_id = person.id
    LEFT JOIN {MOVIE_TABLE} AS film ON person_film.film_work_id = film.id
    WHERE person.modified > %s
    GROUP BY person.id
    ORDER BY modified
    """

    def query(self):
        logger.info(self._query)
        return self._query
