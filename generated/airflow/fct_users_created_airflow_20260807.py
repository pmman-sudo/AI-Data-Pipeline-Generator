from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from airflow.utils.log.logging_helper import log_helper
from datetime import datetime, timedelta
import logging

default_args = {
    'owner': 'Demo',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

def create_table(**kwargs):
    try:
        logging.info('Creating table fct_users_created')
        # code to create table fct_users_created
        logging.info('Table created successfully')
    except Exception as e:
        logging.error(f'Error creating table: {e}')

def load_data(**kwargs):
    try:
        logging.info('Loading data into table fct_users_created')
        # code to load data into table fct_users_created
        logging.info('Data loaded successfully')
    except Exception as e:
        logging.error(f'Error loading data: {e}')

with DAG(
    'fct_users_created_dag',
    default_args=default_args,
    description='A DAG to create and load data into fct_users_created table',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(1),
    tags=['Demo'],
) as dag:
    create_table_task = PythonOperator(
        task_id='create_table',
        python_callable=create_table,
    )
    load_data_task = PythonOperator(
        task_id='load_data',
        python_callable=load_data,
    )
    create_table_task >> load_data_task