from queries.settings import DB_SETTINGS


class Genre:
    query = f"""
    SELECT genre.id, genre.name as title, genre.description, genre.modified as modified
    FROM {DB_SETTINGS.genre_table} as genre
    WHERE genre.modified > %s
    GROUP BY genre.id
    ORDER BY modified
    """
