from datetime import datetime, timedelta

from airflow.models import DAG
from airflow.operators.python import PythonOperator
from models.movie_es import MovieES
from queries.movie import MovieQuery
from wrappers import fetch_wrapper, load_wrapper, transform_wrapper

from settings import APP_SETTINGS

with DAG(
    dag_id=APP_SETTINGS.movie_dag,
    schedule=timedelta(APP_SETTINGS.interval),
    start_date=datetime.min,
    catchup=False,
) as dag:
    task_fetch_movies = PythonOperator(
        task_id="fetch",
        python_callable=fetch_wrapper(MovieQuery, APP_SETTINGS.movie_state_key),
        do_xcom_push=True,
    )
    task_transform_movies = PythonOperator(
        task_id="transform",
        python_callable=transform_wrapper(MovieES),
        do_xcom_push=True,
    )
    task_load_movies = PythonOperator(
        task_id="load",
        python_callable=load_wrapper(APP_SETTINGS.es_movies_index),
        do_xcom_push=True,
    )

    task_fetch_movies >> task_transform_movies >> task_load_movies
