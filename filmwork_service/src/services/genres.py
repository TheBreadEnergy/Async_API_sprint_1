from functools import lru_cache
from uuid import UUID

from elasticsearch import AsyncElasticsearch, NotFoundError
from elasticsearch.helpers import async_scan
from fastapi import Depends
from redis.asyncio import Redis
from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.models.genre import Genre

GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class GenreService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, genre_id: UUID) -> Genre | None:
        genre = await self._genre_from_cache(genre_id)

        if not genre:
            genre = await self._get_genre_from_elastic(genre_id)
            if not genre:
                return None
            await self._put_genre_to_cache(genre)

        return genre

    async def get_all(
        self, sort: str, data_filter: dict, page: int, size: int
    ) -> list[Genre] | None:
        offset_min = (page - 1) * size
        offset_max = page * size
        genres = await self._get_genres_from_elastic(sort, data_filter, page, size)
        return genres[offset_min:offset_max]

    async def search_genre(
        self, query: str, page: int, size: int
    ) -> list[Genre] | None:
        docs = []
        offset_min = (page - 1) * size
        offset_max = page * size

        body_query = {"query": {"match_phrase_prefix": {"name": {"query": query}}}}

        async for doc in async_scan(
            client=self.elastic, query=body_query, index="genres"
        ):
            doc["_source"]["page"] = page
            doc["_source"]["size"] = size
            docs.append(Genre(**doc["_source"]))
        return docs[offset_min:offset_max]

    async def _get_genres_from_elastic(
        self, sort: str, data_filter: dict, page: int, size: int
    ) -> list[Genre] | None:
        body_query = {
            "query": {"bool": {"filter": {"bool": {"must": []}}}},
            "sort": [{"name.raw": {"order": sort}}],
        }

        if "id" in data_filter:
            body_query["query"]["bool"]["filter"]["bool"]["must"].append(
                {"term": {"_id": data_filter["id"]}}
            )

        docs = []
        async for doc in async_scan(
            client=self.elastic, query=body_query, index="genres", preserve_order=True
        ):
            doc["_source"]["page"] = page
            doc["_source"]["size"] = size
            docs.append(Genre(**doc["_source"]))
        return docs

    async def _get_genre_from_elastic(self, genre_id: UUID) -> Genre | None:
        try:
            doc = await self.elastic.get(index="genres", id=str(genre_id))
        except NotFoundError:
            return None

        return Genre(**doc["_source"])

    async def _genre_from_cache(self, genre_id: UUID) -> Genre | None:
        # Пытаемся получить данные жанра из кеша, используя команду get
        data_from_cache = await self.redis.get(f"genre_{genre_id}")
        if not data_from_cache:
            return None

        genre = Genre.parse_raw(data_from_cache)
        return genre

    async def _put_genre_to_cache(self, genre: Genre):
        await self.redis.set(
            f"genre_{genre.id}", genre.json(), GENRE_CACHE_EXPIRE_IN_SECONDS
        )


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
