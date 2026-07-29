"""
This DAG creates a fact table of newly created users.

The DAG extracts the required columns (user_id and user_name) from the Hive dataset logging_events in the PROD environment.
It then loads the data into the fct_users_created table.
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.apache.hive.operators.hive import HiveOperator
from airflow.utils.db import provide_session
from airflow.utils.log.logging_mixin import LoggingMixin
import logging
import json

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

def extract_data(**kwargs):
    """
    Extracts data from the Hive dataset logging_events.

    :param kwargs: Keyword arguments
    :return: None
    """
    logging.info('Extracting data from Hive')
    try:
        # Using HiveOperator to extract data
        HiveOperator(
            task_id='extract_data',
            hive_cli_conn_id='hive_default',
            sql='SELECT user_id, user_name FROM logging_events',
            dag=dag
        )
    except Exception as e:
        logging.error(f'Error extracting data: {e}')

def load_data(**kwargs):
    """
    Loads the extracted data into the fct_users_created table.

    :param kwargs: Keyword arguments
    :return: None
    """
    logging.info('Loading data into fct_users_created')
    try:
        # Using HiveOperator to load data
        HiveOperator(
            task_id='load_data',
            hive_cli_conn_id='hive_default',
            sql='INSERT INTO fct_users_created SELECT user_id, user_name FROM logging_events',
            dag=dag
        )
    except Exception as e:
        logging.error(f'Error loading data: {e}')

with DAG(
    'fct_users_created_dag',
    default_args=default_args,
    description='A DAG to create the fct_users_created fact table',
    schedule_interval='0 8 * * *',
    start_date=datetime(2023, 1, 1),
    catchup=False,
) as dag:
    extract_data_task = PythonOperator(
        task_id='extract_data',
        python_callable=extract_data
    )
    load_data_task = PythonOperator(
        task_id='load_data',
        python_callable=load_data
    )
    extract_data_task >> load_data_task