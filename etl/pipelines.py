from datetime import datetime
from typing import Generator, Union

from elasticsearch import Elasticsearch
from logger import logger
from models.genre_es import GenreES
from models.movie_es import MovieES
from models.person_es import PersonES
from pipeline_common import fetch_generator, save_generator, transform_generator
from psycopg import ServerCursor
from state import State


def build_pipeline(
    pg_cursor: ServerCursor,
    state: State,
    es_client: Elasticsearch,
    query: str,
    es_index: str,
    redis_key: str,
    entity_type: Union[MovieES, GenreES, PersonES],
):
    saver_gen = save_generator(es_index, redis_key)
    transformer_gen = transform_generator(entity_type)
    fetcher_gen = fetch_generator(query)
    saver_coro = saver_gen(es_client, state)
    transformer_coro = transformer_gen(next_node=saver_coro)
    fetcher_coro = fetcher_gen(pg_cursor, next_node=transformer_coro)
    return fetcher_coro


def start_pipeline(state: State, key: str, pipeline: Generator):
    last_update = state.get_state(key) or str(datetime.min)
    logger.info("==== Last update in %s index was %s", key, last_update)
    pipeline.send(last_update)
