from functools import lru_cache
from typing import Optional
from uuid import UUID

from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from elasticsearch.helpers import async_scan
from fastapi import Depends
from models.film import Film, Films
from redis.asyncio import Redis

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, film_id: UUID) -> Optional[Film]:
        film = await self._film_from_cache(film_id)
        if not film:
            film = await self._get_film_from_elastic(film_id)
            if not film:
                return None
            await self._put_film_to_cache(film)
        return film

    async def get_all(
        self, sort: str, data_filter, page, size
    ) -> Optional[list[Films]]:
        offset_min = (page - 1) * size
        offset_max = page * size
        films = await self._get_films_from_elastic(data_filter, sort, page, size)
        return films[offset_min:offset_max]

    async def search_film(
        self, id_film: UUID, title: str, page, size
    ) -> Optional[list[Films]]:
        docs = []
        offset_min = (page - 1) * size
        offset_max = page * size
        if id_film:
            film = await self.get_by_id(id_film)
            if film:
                docs.append(Films(**film.__dict__, size=size, page=page))
                return docs
            else:
                return []
        if title:
            body_query = {
                "query": {"match": {"title": {"query": title, "operator": "and"}}}
            }

            async for doc in async_scan(
                client=self.elastic, query=body_query, index="movies"
            ):
                doc["_source"]["page"] = page
                doc["_source"]["size"] = size
                docs.append(Films(**doc["_source"]))
            return docs[offset_min:offset_max]

        return []

    async def _get_films_from_elastic(
        self, data_filter, sort, page, size
    ) -> Optional[list[Films]]:
        body_query = {"query": {"bool": {"filter": {"bool": {"must": []}}}}}
        if sort:
            if sort.startswith("-"):
                direction_sort = "desc"
                sort = sort[1:]
            else:
                direction_sort = "asc"
            if sort == "title":
                body_query["sort"] = [{"title.raw": direction_sort}]
            if sort == "imdb_rating":
                body_query["sort"] = [{sort: direction_sort}]
        for f_item in data_filter:
            if f_item == "actors" or f_item == "writers" or f_item == "genre":
                body_query["query"]["bool"]["filter"]["bool"]["must"].append(
                    {
                        "nested": {
                            "path": f_item,
                            "query": {"term": {f"{f_item}.id": data_filter[f_item]}},
                        }
                    }
                )
            else:
                body_query["query"]["bool"]["filter"]["bool"]["must"].append(
                    {"term": {f_item: data_filter[f_item]}}
                )
        docs = []
        async for doc in async_scan(
            client=self.elastic, query=body_query, index="movies", preserve_order=True
        ):
            doc["_source"]["page"] = page
            doc["_source"]["size"] = size
            docs.append(Films(**doc["_source"]))
        return docs

    async def _get_film_from_elastic(self, film_id: UUID) -> Optional[Film]:
        try:
            doc = await self.elastic.get(index="movies", id=str(film_id))
        except NotFoundError:
            return None

        return Film(**doc["_source"])

    async def _film_from_cache(self, film_id: UUID) -> Optional[Film]:
        # Пытаемся получить данные о фильме из кеша, используя команду get
        data_from_cache = await self.redis.get(str(film_id))
        if not data_from_cache:
            return None

        film = Film.parse_raw(data_from_cache)
        return film

    async def _put_film_to_cache(self, film: Film):
        await self.redis.set(str(film.id), film.json(), FILM_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
