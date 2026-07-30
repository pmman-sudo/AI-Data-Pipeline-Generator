from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago
from airflow.operators.python import PythonOperator
import logging

default_args = {
    'owner': 'urn:li:corpuser:jdoe, urn:li:corpuser:datahub',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

def load_fct_users_created(**kwargs):
    """
    Loads data into the fct_users_created table.
    
    :param kwargs: Airflow keyword arguments
    :return: None
    """
    try:
        # Load the data from the logging_events table into fct_users_created
        logging.info('Loading data into fct_users_created table')
        # Implement the data loading logic here
        logging.info('Data loaded successfully')
    except Exception as e:
        logging.error(f'Error loading data: {e}')
        raise

with DAG(
    'fct_users_created_dag',
    default_args=default_args,
    description='A DAG to load data into the fct_users_created table',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(1),
    tags=[],
) as dag:
    load_fct_users_created_task = PythonOperator(
        task_id='load_fct_users_created',
        python_callable=load_fct_users_created,
    )

    end_task = BashOperator(
        task_id='end_task',
        bash_command='echo "DAG finished execution"',
    )

    load_fct_users_created_task >> end_task