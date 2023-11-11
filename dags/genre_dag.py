from datetime import datetime, timedelta

from airflow.decorators import dag
from models.genre_es import GenreES
from queries.genre import GenreQuery
from settings import APP_SETTINGS
from wrappers import fetch_wrapper, load_wrapper, transform_wrapper

# TODO: write as closures, remove repeatance


@dag(
    dag_id=APP_SETTINGS.genre_dag,
    start_date=datetime.min,
    schedule=timedelta(APP_SETTINGS.interval),
    catchup=False,
)
def genre_dag():
    fetch_genre_task = fetch_wrapper(GenreQuery().query(), APP_SETTINGS.genre_state_key)
    transform_genre_task = transform_wrapper(GenreES)
    load_genre_task = load_wrapper(APP_SETTINGS.es_genre_index)
    generator = fetch_genre_task()
    generator = transform_genre_task(generator)
    load_genre_task(generator)


dag = genre_dag()
