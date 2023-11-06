from datetime import datetime, timedelta

from airflow.models import DAG
from airflow.operators.python import PythonOperator
from models.person_es import PersonES
from queries.person import PersonQuery
from wrappers import fetch_wrapper, load_wrapper, transform_wrapper

from settings import APP_SETTINGS

# TODO: write as closures, remove repeatance


with DAG(
    dag_id=APP_SETTINGS.person_dag,
    schedule=timedelta(APP_SETTINGS.interval),
    start_date=datetime.min,
    catchup=False,
) as dag:
    task_fetch_genre = PythonOperator(
        task_id="fetch",
        python_callable=fetch_wrapper(PersonQuery, APP_SETTINGS.person_state_key),
        do_xcom_push=True,
    )
    task_transform_genre = PythonOperator(
        task_id="transform",
        python_callable=transform_wrapper(PersonES),
        do_xcom_push=True,
    )
    task_load_genre = PythonOperator(
        task_id="load",
        python_callable=load_wrapper(APP_SETTINGS.es_person_index),
        do_xcom_push=True,
    )

    task_fetch_genre >> task_transform_genre >> task_load_genre
