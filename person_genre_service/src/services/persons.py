from functools import lru_cache
from typing import Optional
from uuid import UUID

from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from elasticsearch.helpers import async_scan
from fastapi import Depends
from models.person import Person
from redis.asyncio import Redis

PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, person_id: UUID) -> Optional[Person]:
        person = await self._person_from_cache(person_id)

        if not person:
            person = await self._get_person_from_elastic(person_id)
            if not person:
                return None
            await self._put_person_to_cache(person)

        return person

    async def get_all(
        self, sort: str, data_filter: dict, page: int, size: int
    ) -> Optional[list[Person]]:
        offset_min = (page - 1) * size
        offset_max = page * size
        persons = await self._get_persons_from_elastic(sort, data_filter, page, size)
        return persons[offset_min:offset_max]

    async def _get_persons_from_elastic(
        self, sort: str, data_filter: dict, page: int, size: int
    ) -> Optional[list[Person]]:
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
            client=self.elastic, query=body_query, index="persons", preserve_order=True
        ):
            doc["_source"]["page"] = page
            doc["_source"]["size"] = size
            docs.append(Person(**doc["_source"]))
        return docs

    async def search_person(
        self, query: str, page: int, size: int
    ) -> Optional[list[Person]]:
        docs = []
        offset_min = (page - 1) * size
        offset_max = page * size

        body_query = {"query": {"match_phrase_prefix": {"name": {"query": query}}}}

        async for doc in async_scan(
            client=self.elastic, query=body_query, index="persons"
        ):
            doc["_source"]["page"] = page
            doc["_source"]["size"] = size
            docs.append(Person(**doc["_source"]))
        return docs[offset_min:offset_max]

    async def _get_person_from_elastic(self, person_id: UUID) -> Optional[Person]:
        try:
            doc = await self.elastic.get(index="persons", id=str(person_id))
        except NotFoundError:
            return None

        return Person(**doc["_source"])

    async def _person_from_cache(self, person_id: str) -> Optional[Person]:
        # Пытаемся получить данные персоны из кеша, используя команду get
        data_from_cache = await self.redis.get(str(person_id))
        if not data_from_cache:
            return None

        person = Person.parse_raw(data_from_cache)
        return person

    async def _put_person_to_cache(self, person: Person):
        await self.redis.set(
            str(person.id), person.json(), PERSON_CACHE_EXPIRE_IN_SECONDS
        )


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
