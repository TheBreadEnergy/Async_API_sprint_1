from queries.base import BaseQuery
from queries.settings import DB_SETTINGS


class GenreQuery(BaseQuery):
    _query = f"""
    SELECT genre.id, genre.name as title, genre.description, genre.modified as modified
    FROM {DB_SETTINGS.genre_table} as genre
    WHERE genre.modified > %s
    GROUP BY genre.id
    ORDER BY modified
    """

    def query(self):
        return self._query
