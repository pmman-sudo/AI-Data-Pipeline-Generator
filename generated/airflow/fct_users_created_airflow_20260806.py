from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from airflow.utils.log.logging_mixin import LoggingMixin
import logging

default_args = {
    'owner': 'Demo',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'fct_users_created_dag',
    default_args=default_args,
    description='A DAG to load fct_users_created table',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(1),
    tags=['Demo'],
)

def load_fct_users_created(**kwargs):
    """Loads data into fct_users_created table"""
    try:
        logging.info('Loading data into fct_users_created table')
        # Load data into fct_users_created table
        # For demonstration purposes, this is a placeholder
        # Replace with actual code to load data
        logging.info('Data loaded successfully')
    except Exception as e:
        logging.error(f'Error loading data: {str(e)}')
        raise

load_task = PythonOperator(
    task_id='load_fct_users_created',
    python_callable=load_fct_users_created,
    dag=dag,
)