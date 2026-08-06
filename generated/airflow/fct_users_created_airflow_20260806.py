from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.operators.redshift import RedshiftOperator
import logging

default_args = {
    'owner': ['Demo'],
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

def load_data(**kwargs):
    """
    Load data into the fct_users_created table.
    """
    try:
        logging.info('Loading data into fct_users_created table')
        # Load data logic here
        logging.info('Data loaded successfully')
    except Exception as e:
        logging.error(f'Error loading data: {e}')
        raise

with DAG(
    'fct_users_created_dag',
    default_args=default_args,
    description='A DAG to load data into the fct_users_created table',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    tags=['Demo'],
) as dag:
    load_data_task = PythonOperator(
        task_id='load_data',
        python_callable=load_data,
    )

    end_task = RedshiftOperator(
        task_id='end_task',
        redshift_conn_id='redshift_default',
        sql='SELECT 1',
    )

    load_data_task >> end_task