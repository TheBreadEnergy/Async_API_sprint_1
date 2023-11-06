import json
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
from queries.base import BaseQuery

from settings import APP_SETTINGS, ES_DSN


def fetch_wrapper(query_class: BaseQuery, state_key: str):
    @task
    def fetch(ti: TaskInstance):
        pg_hook = PostgresHook(
            postgres_conn_id=APP_SETTINGS.postgres_connection_id,
            options=APP_SETTINGS.options,
        )
        with closing(pg_hook.get_conn()) as conn, conn.cursor() as cursor:
            last_updated = ti.xcom_pull(key=state_key, include_prior_dates=True) or str(
                datetime.min
            )
            # TODO: logging
            cursor.execute(query_class.query(), (last_updated,))
            while items := cursor.fetchmany(APP_SETTINGS.batch_size):
                json_data = json.dumps([dict(x) for x in items], indent=4)
                ti.xcom_push(
                    key=state_key,
                    value=str(items[-1]["modified"]),
                )
                yield json_data

    return fetch


def transform_wrapper(mapping: tp.Union[MovieES, GenreES, PersonES]):
    @task
    def transform(ti: TaskInstance):
        json_data = ti.xcom_pull(task_ids="fetch")
        data = json.loads(json_data)
        batch = []
        for item in data:
            movie = mapping(**item).model_dump()
            movie["_id"] = movie["id"]
            batch.append(movie)
        json_data = json.dumps(batch, indent=4)
        return json_data

    return transform


def load_wrapper(es_index: str):
    @task
    def load(ti: TaskInstance):
        json_data = ti.xcom_pull(task_ids="transform")
        if not json_data:
            return
        data = json.loads(json_data)
        es_dsn = f"http://{ES_DSN.host}: {ES_DSN.port}"
        with closing(Elasticsearch([es_dsn])) as client:
            lines, _ = helpers.bulk(
                client=client,
                actions=data,
                index=es_index,
                chunk_size=APP_SETTINGS.batch_size,
            )

            # TODO: add logging
            return len(data)

    return load
