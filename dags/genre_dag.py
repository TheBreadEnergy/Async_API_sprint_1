from datetime import datetime

from airflow.decorators import dag
from airflow.operators.python import PythonOperator
from models.genre_es import GenreES
from queries.genre import GenreQuery
from wrappers import fetch_wrapper, load_wrapper, transform_wrapper

from settings import APP_SETTINGS

# TODO: write as closures, remove repeatance


@dag(dag_id=APP_SETTINGS.genre_dag, start_date=datetime.min, catchup=False)
def genre_dag():
    fetch_operator = PythonOperator(
        task_id="fetch",
        python_callable=fetch_wrapper(GenreQuery, APP_SETTINGS.genre_state_key),
        do_xcom_push=True,
    )
    transfom_operator = PythonOperator(
        task_id="transform",
        python_callable=transform_wrapper(GenreES),
        do_xcom_push=True,
    )
    load_operator = PythonOperator(
        task_id="load", python_callable=load_wrapper(APP_SETTINGS.es_genre_index)
    )

    fetch_operator >> transfom_operator >> load_operator


dag = genre_dag()
