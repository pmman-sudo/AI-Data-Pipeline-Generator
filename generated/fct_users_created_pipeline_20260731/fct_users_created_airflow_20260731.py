from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
import logging

default_args = {
    'owner': 'urn:li:corpuser:jdoe, urn:li:corpuser:datahub',
    'depends_on_past': False,
    'start_date': datetime(2023, 12, 1),
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,
}

dag = DAG(
    'fct_users_created_dag',
    default_args=default_args,
    schedule_interval=timedelta(days=1),
)

def extract_data(**kwargs):
    """
    Extract data from logging_events table in Hive.
    """
    logging.info('Extracting data from logging_events table')
    # implement data extraction logic here
    return True

def transform_data(**kwargs):
    """
    Transform extracted data into required format for fct_users_created table.
    """
    logging.info('Transforming data for fct_users_created table')
    # implement data transformation logic here
    return True

def load_data(**kwargs):
    """
    Load transformed data into fct_users_created table.
    """
    logging.info('Loading data into fct_users_created table')
    # implement data loading logic here
    return True

extract_task = PythonOperator(
    task_id='extract_data',
    python_callable=extract_data,
    dag=dag,
)

transform_task = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    dag=dag,
)

load_task = PythonOperator(
    task_id='load_data',
    python_callable=load_data,
    dag=dag,
)

end_task = BashOperator(
    task_id='end_task',
    bash_command='echo "DAG completed successfully"',
    dag=dag,
)

extract_task >> transform_task >> load_task >> end_task