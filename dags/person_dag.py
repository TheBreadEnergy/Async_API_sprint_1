import logging
from datetime import datetime, timedelta

from airflow.models import DAG
from models.person_es import PersonES
from queries.person import PersonQuery
from settings import APP_SETTINGS
from wrappers import fetch_wrapper, load_wrapper, transform_wrapper

# TODO: write as closures, remove repeatance
logger = logging.getLogger(__name__)
with DAG(
    dag_id=APP_SETTINGS.person_dag,
    schedule=timedelta(APP_SETTINGS.interval),
    start_date=datetime.min,
    catchup=False,
) as dag:
    fetch_person_task = fetch_wrapper(
        PersonQuery().query(), APP_SETTINGS.person_state_key
    )
    logger.info(PersonQuery().query())
    transform_person_task = transform_wrapper(PersonES)
    load_person_task = load_wrapper(APP_SETTINGS.es_person_index)
    json_data = fetch_person_task()
    json_data = transform_person_task(json_data)
    load_person_task(json_data)
