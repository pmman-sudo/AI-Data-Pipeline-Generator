from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
import logging
import json

default_args = {
    'owner': 'Demo',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'ingest_fct_users_created',
    default_args=default_args,
    description='Ingest fct_users_created table every day at midnight',
    schedule_interval='@daily',
    start_date=datetime(2023, 12, 1),
    tags=['Demo']
)

def ingest_fct_users_created(**kwargs):
    """
    Ingest fct_users_created table.

    :param kwargs: Keyword arguments
    :return: None
    """
    try:
        # Establish a connection to the database
        # TODO: Replace with your actual database connection
        conn = None

        # Ingest the fct_users_created table
        # TODO: Replace with your actual ingestion logic
        logging.info('Ingesting fct_users_created table')
        conn.cursor().execute('SELECT * FROM fct_users_created')
        logging.info('Ingestion complete')

    except Exception as e:
        logging.error(f'Error ingesting fct_users_created table: {e}')
        raise

ingest_fct_users_created_task = PythonOperator(
    task_id='ingest_fct_users_created',
    python_callable=ingest_fct_users_created,
    dag=dag
)