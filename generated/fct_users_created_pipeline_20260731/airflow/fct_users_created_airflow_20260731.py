from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.transfers.hive import HiveOperator
from airflow.utils.db import provide_session
from airflow.utils.log import LoggingMixin
from airflow.utils.task_group import TaskGroup
from airflow.hooks.base import BaseHook
import logging
from structlog import wrap_logger

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

logger = wrap_logger(logging.getLogger(__name__))

def fetch_data(**kwargs):
    """
    Fetch data from logging_events table.
    """
    try:
        # Initialize Hive hook
        hive_hook = HiveOperator(
            task_id='fetch_data',
            hive_cli_conn_id='hive_default',
            sql='SELECT * FROM logging_events',
            dag=dag
        )
        
        # Execute Hive query and fetch results
        results = hive_hook.execute()['output']
        
        # Log results
        logger.info('Fetched data from logging_events table.')
        
        return results
    
    except Exception as e:
        # Log error and raise exception
        logger.error('Error fetching data from logging_events table: %s', str(e))
        raise

def process_data(**kwargs):
    """
    Process fetched data and create fct_users_created records.
    """
    try:
        # Get fetched data from XCom
        data = kwargs['ti'].xcom_pull(task_ids='fetch_data')
        
        # Process data
        processed_data = []
        for row in data:
            user_id = row[0]
            user_name = row[1]
            processed_data.append({
                'user_id': user_id,
                'user_name': user_name
            })
        
        # Log processed data
        logger.info('Processed data for fct_users_created table.')
        
        return processed_data
    
    except Exception as e:
        # Log error and raise exception
        logger.error('Error processing data for fct_users_created table: %s', str(e))
        raise

def load_data(**kwargs):
    """
    Load processed data into fct_users_created table.
    """
    try:
        # Get processed data from XCom
        data = kwargs['ti'].xcom_pull(task_ids='process_data')
        
        # Initialize Hive hook
        hive_hook = HiveOperator(
            task_id='load_data',
            hive_cli_conn_id='hive_default',
            sql='CREATE TABLE IF NOT EXISTS fct_users_created (user_id VARCHAR(100), user_name BOOLEAN)',
            dag=dag
        )
        
        # Load data into fct_users_created table
        hive_hook = HiveOperator(
            task_id='load_data',
            hive_cli_conn_id='hive_default',
            sql='INSERT INTO fct_users_created VALUES (%s, %s)',
            params=data,
            dag=dag
        )
        
        # Log loaded data
        logger.info('Loaded data into fct_users_created table.')
        
    except Exception as e:
        # Log error and raise exception
        logger.error('Error loading data into fct_users_created table: %s', str(e))
        raise

with DAG(
    'fct_users_created_dag',
    default_args=default_args,
    description='A DAG to generate fct_users_created table',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    catchup=False,
) as dag:
    
    fetch_data_task = PythonOperator(
        task_id='fetch_data',
        python_callable=fetch_data,
    )
    
    process_data_task = PythonOperator(
        task_id='process_data',
        python_callable=process_data,
    )
    
    load_data_task = PythonOperator(
        task_id='load_data',
        python_callable=load_data,
    )
    
    fetch_data_task >> process_data_task >> load_data_task