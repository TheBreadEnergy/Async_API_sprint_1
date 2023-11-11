import time
from datetime import datetime
from typing import Generator, Tuple, Union

import backoff
from common.coroutine import coroutine
from elasticsearch import Elasticsearch, helpers
from logger import logger
from models.genre_es import GenreES
from models.movie_es import MovieES
from models.person_es import PersonES
from psycopg import ServerCursor
from state import State

from config import APP_SETTINGS, BACKOFF_CONFIG


def fetch_generator(query: str):
    @coroutine
    @backoff.on_exception(**BACKOFF_CONFIG)
    def fetch(cursor: ServerCursor, next_node: Generator) -> Generator[None, str, None]:
        while last_updated := (yield):
            logger.info(
                "Quering entities with modified date greater than %s, with query %s",
                last_updated,
                query,
            )
            cursor.execute(query, (last_updated,))
            while result := cursor.fetchmany(size=APP_SETTINGS.batch_size):
                logger.info("Queried %s objects", len(result))
                next_node.send(result)

    return fetch


def transform_generator(entity_type: Union[MovieES, GenreES, PersonES]):
    @coroutine
    def transform(next_node: Generator) -> Generator[None, list[dict], None]:
        while data := (yield):
            logger.info("Transformation step started")
            batch = []
            logger.info(data)
            for entity_dict in data:
                entity = entity_type(**entity_dict).model_dump()
                entity["_id"] = entity["id"]
                batch.append(entity)
            update_date = data[-1]["modified"]
            logger.info("Transformed %s records", len(data))
            next_node.send((batch, update_date))

    return transform


def save_generator(index: str, state_key: str):
    @coroutine
    @backoff.on_exception(**BACKOFF_CONFIG)
    def save(
        es_client: Elasticsearch, state: State
    ) -> Generator[None, Tuple[list[dict], datetime], None]:
        while movies := (yield):
            logger.info("Save state begins")
            t = time.perf_counter()
            lines, _ = helpers.bulk(
                client=es_client,
                actions=movies[0],
                index=index,
                chunk_size=APP_SETTINGS.batch_size,
            )
            elapsed = time.perf_counter() - t
            if lines == 0:
                logger.info("Nothing to update in index %s", index)
            else:
                logger.info(
                    "%s lines was updated in %s, for index %s", lines, elapsed, index
                )

            modified = movies[1]
            state.set_state(state_key, str(modified))
            logger.info("ES state was changed to %s date", modified)

    return save
