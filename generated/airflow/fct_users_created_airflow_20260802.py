from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import logging

default_args = {
    'owner': 'Demo',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

def load_fct_users_created(**kwargs):
    """
    Load data into fct_users_created table.
    """
    try:
        # Simulating data load, replace with actual data load logic
        logging.info("Loading data into fct_users_created table")
    except Exception as e:
        logging.error(f"Error loading data: {str(e)}")
        raise

with DAG(
    'fct_users_created_dag',
    default_args=default_args,
    description='DAG to load data into fct_users_created table',
    schedule_interval='@daily',
    start_date=days_ago(1),
    tags=['Demo'],
) as dag:
    load_fct_users_created_task = PythonOperator(
        task_id='load_fct_users_created',
        python_callable=load_fct_users_created,
    )