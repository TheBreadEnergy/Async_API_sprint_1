from queries.base import BaseQuery
from queries.settings import DB_SETTINGS


class PersonQuery(BaseQuery):
    _query = f"""
    SELECT person.id, person.full_name AS name, person.gender AS gender,
    ARRAY_AGG(
    DISTINCT jsonb_build_object('id', film.id, 'title', film.title, 'role': person_film.role)) AS film_roles,
    person.modified AS modified,
    FROM {DB_SETTINGS.person_table} AS person
    LEFT JOIN {DB_SETTINGS.movie_person_table} AS person_film ON person_film.person_id = person.id
    LEFT JOIN {DB_SETTINGS.movie_table} AS film ON person_film.film_work_id = film.id
    WHERE person.modified > %s
    GROUP BY person.id
    ORDER BY modified
    """

    def query(self):
        return self._query
