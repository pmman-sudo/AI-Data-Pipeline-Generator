from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.hooks.base import BaseHook
from airflow.utils.db import provide_session
from airflow.utils.log.logging_mixin import LoggingMixin
from airflow.exceptions import AirflowException
import json
import logging

default_args = {
    'owner': 'urn:li:corpuser:jdoe, urn:li:corpuser:datahub',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,
}

def fetch_data(**kwargs):
    """
    Fetch data from the upstream dataset.
    
    :param kwargs: Airflow context
    :return: None
    """
    try:
        # Initialize logging
        logger = LoggingMixin().log
        logger.info('Fetching data from upstream dataset')
        
        # Fetch data from Hive
        hive_conn = BaseHook.get_connection('hive_default')
        cursor = hive_conn.get_cursor()
        cursor.execute('SELECT * FROM logging_events')
        data = cursor.fetchall()
        
        # Process data
        processed_data = []
        for row in data:
            user_id = row[0]
            user_name = bool(row[1])  # Convert to boolean
            processed_data.append((user_id, user_name))
        
        # Log the number of records fetched
        logger.info(f'Fetched {len(data)} records')
        
        # Store the processed data in XCom
        kwargs['ti'].xcom_push(key='processed_data', value=processed_data)
    
    except AirflowException as e:
        logger.error(f'Error fetching data: {e}')
        raise

def load_data(**kwargs):
    """
    Load the processed data into the fct_users_created table.
    
    :param kwargs: Airflow context
    :return: None
    """
    try:
        # Initialize logging
        logger = LoggingMixin().log
        logger.info('Loading data into fct_users_created table')
        
        # Get the processed data from XCom
        processed_data = kwargs['ti'].xcom_pull(key='processed_data', task_ids='fetch_data')
        
        # Load data into the table
        hive_conn = BaseHook.get_connection('hive_default')
        cursor = hive_conn.get_cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS fct_users_created (user_id varchar(100), user_name boolean)')
        cursor.executemany('INSERT INTO fct_users_created VALUES (%s, %s)', processed_data)
        
        # Log the number of records loaded
        logger.info(f'Loaded {len(processed_data)} records')
    
    except AirflowException as e:
        logger.error(f'Error loading data: {e}')
        raise

dag = DAG(
    'fct_users_created_dag',
    default_args=default_args,
    description='A DAG to create the fct_users_created table',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    catchup=False,
)

fetch_data_task = PythonOperator(
    task_id='fetch_data',
    python_callable=fetch_data,
    dag=dag,
)

load_data_task = PythonOperator(
    task_id='load_data',
    python_callable=load_data,
    dag=dag,
)

end_task = DummyOperator(
    task_id='end_task',
    trigger_rule='all_done',
    dag=dag,
)

fetch_data_task >> load_data_task >> end_task