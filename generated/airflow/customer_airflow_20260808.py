from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.operators.redshift import RedshiftOperator
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
    """
    Extract customer data from the customer table.
    """
    try:
        # Simulating data extraction
        data = {
            'user_id': [1, 2, 3],
            'created_at': [datetime(2022, 1, 1), datetime(2022, 1, 2), datetime(2022, 1, 3)],
            'email': ['user1@example.com', 'user2@example.com', 'user3@example.com']
        }
        logging.info('Data extracted successfully')
        return data
    except Exception as e:
        logging.error(f'Error extracting data: {e}')
        raise

def load_data(**kwargs):
    """
    Load customer data into the customer table.
    """
    try:
        data = kwargs['task_instance'].xcom_pull(task_ids='extract_data')
        # Simulating data loading
        logging.info('Data loaded successfully')
    except Exception as e:
        logging.error(f'Error loading data: {e}')
        raise

with DAG(
    'customer_orders',
    default_args=default_args,
    description='A DAG to manage customer orders',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2022, 1, 1),
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
    end_task = RedshiftOperator(
        task_id='end_task',
        redshift_conn_id='aws_default',
        sql='SELECT 1',
    )
    extract_data_task >> load_data_task >> end_task