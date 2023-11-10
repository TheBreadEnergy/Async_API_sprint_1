from datetime import datetime, timedelta

from airflow.models import DAG
from models.movie_es import MovieES
from queries.movie import MovieQuery
from settings import APP_SETTINGS
from wrappers import fetch_batch_wrapper, load_wrapper, transform_wrapper

with DAG(
    dag_id=APP_SETTINGS.movie_dag,
    schedule=timedelta(APP_SETTINGS.interval),
    start_date=datetime.min,
    catchup=False,
) as dag:
    fetch_movies_task = fetch_batch_wrapper(
        MovieQuery().query(), APP_SETTINGS.movie_state_key
    )
    transform_movies_task = transform_wrapper(MovieES)
    load_movies_task = load_wrapper(APP_SETTINGS.es_movies_index)
    while data := fetch_movies_task():
        data = transform_movies_task(data)
        load_movies_task(data)
