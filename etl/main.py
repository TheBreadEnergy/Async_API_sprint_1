import time
from contextlib import closing

import backoff
import psycopg
from elasticsearch import Elasticsearch
from logger import logger
from models.genre_es import GenreES
from models.movie_es import MovieES
from models.person_es import PersonES
from pipelines import build_pipeline, start_pipeline
from psycopg import ServerCursor
from psycopg.conninfo import make_conninfo
from psycopg.rows import dict_row
from queries.genre import GenreQuery
from queries.movie import MovieQuery
from queries.person import PersonQuery
from redis import Redis
from redis_storage import RedisStorage
from state import State

from config import APP_SETTINGS, BACKOFF_CONFIG, ELASTIC_DSN, POSTGRES_DSN, REDIS_DSN


@backoff.on_exception(**BACKOFF_CONFIG)
def main() -> None:
    postgres_dsn = make_conninfo(**POSTGRES_DSN.model_dump())
    elastic_dsn = f"http://{ELASTIC_DSN.host}:{ELASTIC_DSN.port}"
    redis_client = Redis(**REDIS_DSN.model_dump())
    state = State(
        RedisStorage(
            redis_adapter=redis_client, logger=logger, name=APP_SETTINGS.root_key
        )
    )

    with closing(
        psycopg.connect(postgres_dsn, row_factory=dict_row)
    ) as connection, ServerCursor(connection, "fetcher") as cursor, closing(
        Elasticsearch([elastic_dsn])
    ) as es_client:
        movie_pipeline = build_pipeline(
            pg_cursor=cursor,
            state=state,
            es_client=es_client,
            query=MovieQuery().query(),
            es_index=APP_SETTINGS.movie_index,
            redis_key=APP_SETTINGS.movie_key,
            entity_type=MovieES,
        )
        genre_pipeline = build_pipeline(
            pg_cursor=cursor,
            state=state,
            es_client=es_client,
            query=GenreQuery().query(),
            es_index=APP_SETTINGS.genre_index,
            redis_key=APP_SETTINGS.genre_key,
            entity_type=GenreES,
        )
        person_pipeline = build_pipeline(
            pg_cursor=cursor,
            state=state,
            es_client=es_client,
            query=PersonQuery().query(),
            es_index=APP_SETTINGS.person_index,
            redis_key=APP_SETTINGS.person_key,
            entity_type=PersonES,
        )
        pipelines = {
            APP_SETTINGS.movie_key: movie_pipeline,
            APP_SETTINGS.genre_key: genre_pipeline,
            APP_SETTINGS.person_key: person_pipeline,
        }
        while True:
            for key, pipeline in pipelines.items():
                start_pipeline(state=state, key=key, pipeline=pipeline)
            time.sleep(APP_SETTINGS.scan_frequency)


if __name__ == "__main__":
    main()
