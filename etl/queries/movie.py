from queries.base import BaseQuery
from queries.settings import (
    GENRE_MOVIE_TABLE,
    GENRE_TABLE,
    MOVIE_TABLE,
    PERSON_MOVIE_TABLE,
    PERSON_TABLE,
)


class MovieQuery(BaseQuery):
    _query = f"""
        SELECT film.id, film.rating as imdb_rating, film.title, film.description,
        ARRAY_AGG(DISTINCT genre.name) as genre,
        ARRAY_AGG(DISTINCT person.full_name) FILTER (WHERE person_film.role = 'director') as director,
        ARRAY_AGG(DISTINCT person.full_name) FILTER (WHERE person_film.role = 'actor') as actors_names,
        ARRAY_AGG(DISTINCT person.full_name) FILTER (WHERE person_film.role = 'screenwriter') as writers_names,
        ARRAY_AGG(
            DISTINCT jsonb_build_object('id', person.id, 'name', person.full_name))
        FILTER (WHERE person_film.role = 'actor') as actors,
        ARRAY_AGG(
            DISTINCT jsonb_build_object('id', person.id, 'name', person.full_name))
        FILTER (WHERE person_film.role = 'screenwriter') as writers,
        ARRAY_AGG( 
            DISTINCT jsonb_build_object('id', genre.id, 'name', genre.name)
        ) as genres,
        GREATEST (film.modified, MAX(genre.modified), MAX(person.modified)) as modified
        FROM {MOVIE_TABLE} film
        LEFT JOIN {GENRE_MOVIE_TABLE} as genre_film ON genre_film.film_work_id = film.id
        LEFT JOIN {GENRE_TABLE} as genre ON  genre_film.genre_id = genre.id
        LEFT JOIN {PERSON_MOVIE_TABLE} as person_film ON person_film.film_work_id = film.id
        LEFT JOIN {PERSON_TABLE} as person ON person_film.person_id = person.id
        WHERE GREATEST(film.modified, genre.modified, person.modified) > %s
        GROUP BY film.id
        ORDER BY modified
        """

    def query(self):
        return self._query