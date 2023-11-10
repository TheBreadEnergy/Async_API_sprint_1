import json
import logging
import typing as tp
from contextlib import closing
from datetime import datetime

from airflow.decorators import task
from airflow.models import TaskInstance
from airflow.providers.postgres.hooks.postgres import PostgresHook
from elasticsearch import Elasticsearch, helpers
from models.genre_es import GenreES
from models.movie_es import MovieES
from models.person_es import PersonES
from psycopg2.extras import DictCursor
from settings import APP_SETTINGS, ES_DSN

logger = logging.getLogger(__name__)


def fetch_wrapper(query: str, state_key: str):
    @task.python()
    def fetch(ti: TaskInstance = None):
        pg_hook = PostgresHook(postgres_conn_id=APP_SETTINGS.postgres_connection_id)
        connection = pg_hook.get_conn()
        cursor = connection.cursor(cursor_factory=DictCursor)
        last_updated = ti.xcom_pull(key=state_key, include_prior_dates=True) or str(
            datetime.min
        )
        cursor.execute(query, (last_updated,))
        items = cursor.fetchall()
        items = [dict(item) for item in items]
        if items:
            ti.xcom_push(key=state_key, value=str(items[-1]["modified"]))
        return items

    return fetch


def transform_wrapper(mapping: tp.Union[MovieES, GenreES, PersonES]):
    @task.python()
    def transform(data: list):
        batch = []
        for item in data:
            entity = mapping(**item).model_dump()
            entity["id"] = str(entity["id"])
            entity["_id"] = entity["id"]
            batch.append(entity)
        json_data = json.dumps(batch, indent=4)
        return json_data

    return transform


def load_wrapper(es_index: str):
    @task.python()
    def load(json_data: str):
        data = json.loads(json_data)
        if not data:
            return
        es_dsn = f"http://{ES_DSN.host}:{ES_DSN.port}"
        with closing(Elasticsearch([es_dsn])) as client:
            lines, _ = helpers.bulk(
                client=client,
                actions=data,
                index=es_index,
                chunk_size=APP_SETTINGS.batch_size,
            )
            # TODO: add logging
            return lines

    return load


def fetch_batch_wrapper(query: str, state_key: str):
    @task
    def fetch_generator(ti: TaskInstance = None) -> tp.Generator:
        pg_hook = PostgresHook(postgres_conn_id=APP_SETTINGS.postgres_connection_id)
        connection = pg_hook.get_conn()
        cursor = connection.cursor("named_cursor")
        last_updated = ti.xcom_pull(key=state_key, include_prior_dates=True) or str(
            datetime.min
        )
        cursor.execute(query, (last_updated,))
        while items := cursor.fetchmany(APP_SETTINGS.batch_size):
            items = [dict(item) for item in items]
            ti.xcom_push(key=state_key, value=str(items[-1]["modified"]))
            yield items

    return fetch_generator
