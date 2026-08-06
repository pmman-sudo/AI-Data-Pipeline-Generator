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

def extract_data(**kwargs):
    try:
        # Simulating data extraction for demonstration purposes
        data = [
            {'user_id': 1, 'created_at': datetime.now(), 'email': 'user1@example.com'},
            {'user_id': 2, 'created_at': datetime.now(), 'email': 'user2@example.com'},
        ]
        return data
    except Exception as e:
        logging.error(f"Error extracting data: {e}")
        raise

def load_data(**kwargs):
    try:
        data = kwargs['ti'].xcom_pull(task_ids='extract_data')
        # Simulating data loading for demonstration purposes
        logging.info(f"Loading data: {data}")
    except Exception as e:
        logging.error(f"Error loading data: {e}")
        raise

with DAG(
    'fct_users_created',
    default_args=default_args,
    description='A DAG for fct_users_created',
    schedule_interval=None,
    start_date=days_ago(1),
    tags=['Demo'],
) as dag:
    extract_data_task = PythonOperator(
        task_id='extract_data',
        python_callable=extract_data,
    )
    load_data_task = PythonOperator(
        task_id='load_data',
        python_callable=load_data,
    )
    extract_data_task >> load_data_task