import json
from contextlib import closing
from datetime import datetime, timedelta

from airflow.models import TaskInstance
from airflow.models import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from elasticsearch import helpers, Elasticsearch

from models.movie_es import MovieES
from settings import APP_SETTINGS, ES_DSN
from queries.movie import MovieQuery


def fetch(ti: TaskInstance):
    pg_hook = PostgresHook(
        postgres_conn_id=APP_SETTINGS.postgres_connection_id,
        options=APP_SETTINGS.options,
    )
    with closing(pg_conn := pg_hook.get_conn()) as conn, conn.cursor() as cursor:
        last_updated = ti.xcom_pull(
            key=APP_SETTINGS.movie_state_key, include_prior_dates=True
        ) or str(datetime.min)
        # TODO: logging
        cursor.execute(MovieQuery.query)
        while items := cursor.fetchmany(APP_SETTINGS.batch_size):
            json_data = json.dumps([dict(x) for x in items], indent=4)
            ti.xcom_push(
                key=APP_SETTINGS.movie_state_key, value=str(items[-1]["modified"]),
            )
            yield json_data


def transform(ti: TaskInstance):
    json_data = ti.xcom_pull(task_ids="fetch")
    data = json.loads(json_data)
    batch = []
    for item in data:
        movie = MovieES(**item).model_dump()
        movie["_id"] = movie["id"]
        batch.append(movie)
    json_data = json.dumps(batch, indent=4)
    return json_data


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
            index=APP_SETTINGS.es_movies_index,
            chunk_size=APP_SETTINGS.batch_size,
        )

        # TODO: add logging
        return len(data)


with DAG(
    dag_id=APP_SETTINGS.movie_dag,
    schedule=timedelta(APP_SETTINGS.interval),
    start_date=datetime.min,
    catchup=False,
):
    task_fetch_movies = PythonOperator(
        task_id="fetch", python_callable=fetch, do_xcom_push=True
    )
    task_transform_movies = PythonOperator(
        task_id="transform", python_callable=transform, do_xcom_push=True,
    )
    task_load_movies = PythonOperator(
        task_id="load", python_callable=load, do_xcom_push=True
    )

    task_fetch_movies >> task_transform_movies >> task_load_movies
