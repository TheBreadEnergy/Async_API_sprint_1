from queries.settings import DB_SETTINGS


class MovieQuery:

    query = f"""
        SELECT film.id, film.rating as imdb_rating, film.title, film.description,
        ARRAY_AGG(DISTINCT genre.name) as genre,
        ARRAY_AGG(DISTINCT person.full_name) FILTER (WHERE person_film.role = 'director') as director,
        ARRAY_AGG(DISTINCT person_full_name) FILTER (WHERE person_film.role = 'actor') as actors_names,
        ARRAY_AGG(DISTINCT person.full_name) FILTER (WHERE person_film.role = 'screenwriter') as writers_names,
        ARRAY_AGG(
            DISTINCT jsonb_build_object('id', person.id, 'name', person.full_name))
        FILTER (WHERE person_film.role = 'actor') as actors,
        ARRAY_AGG(
            DISTINCT jsonb_build_object('id', person.id, 'name', person.full_name))
        FILTER (WHERE person_film.role = 'screenwriter') as writers,
        GREATEST (film.modified, MAX(genre.modified), MAX(person.modified)) as modified
        FROM {DB_SETTINGS.movie_table} film
        LEFT JOIN {DB_SETTINGS.movie_genre_table} as genre_film ON genre_film.film_work_id = film.id
        LEFT JOIN {DB_SETTINGS.genre_table} as genre ON  genre_film.genre_id = genre.id
        LEFT JOIN {DB_SETTINGS.movie_person_table} as person_film ON person_film.film_work_id = film.id
        LEFT JOIN {DB_SETTINGS.person_table} as person ON person_film.person_id = person.id
        WHERE GREATEST(film.modified, genre.modified, person.modified) > %s
        GROUP BY film.id
        ORDER BY modified
        """
