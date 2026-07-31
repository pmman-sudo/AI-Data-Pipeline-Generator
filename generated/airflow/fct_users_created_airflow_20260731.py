from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.operators.aws_sql import AWS_SQLOperator
from airflow.providers.amazon.aws.helpers.sql import build_sql_query
from airflow.utils.db import provide_session
from airflow.hooks.base import BaseHook
from airflow.exceptions import AirflowSkipException
import logging
import json

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

def create_fct_users_created(**kwargs):
    """
    Creates the fct_users_created table.
    """
    logging.info("Creating fct_users_created table")
    query = """
        CREATE TABLE IF NOT EXISTS fct_users_created (
            user_id VARCHAR(100),
            user_name BOOLEAN
        );
    """
    AWS_SQLOperator(
        task_id='create_fct_users_created',
        query=query,
        aws_conn_id='aws_default',
        database='hive',
        params={}
    ).execute(kwargs)

def load_data(**kwargs):
    """
    Loads data from logging_events into fct_users_created.
    """
    logging.info("Loading data into fct_users_created table")
    query = """
        INSERT INTO fct_users_created (user_id, user_name)
        SELECT user_id, user_name
        FROM logging_events;
    """
    AWS_SQLOperator(
        task_id='load_data',
        query=query,
        aws_conn_id='aws_default',
        database='hive',
        params={}
    ).execute(kwargs)

def check_data(**kwargs):
    """
    Checks if data was loaded successfully.
    """
    logging.info("Checking data in fct_users_created table")
    query = """
        SELECT COUNT(*) 
        FROM fct_users_created;
    """
    result = AWS_SQLOperator(
        task_id='check_data',
        query=query,
        aws_conn_id='aws_default',
        database='hive',
        params={}
    ).execute(kwargs)
    if result == 0:
        raise AirflowSkipException("No data loaded")

dag = DAG(
    dag_id='fct_users_created',
    default_args=default_args,
    description='A DAG to create and load the fct_users_created table',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    catchup=False,
)

create_table = PythonOperator(
    task_id='create_table',
    python_callable=create_fct_users_created,
    dag=dag
)

load_data_task = PythonOperator(
    task_id='load_data',
    python_callable=load_data,
    dag=dag
)

check_data_task = PythonOperator(
    task_id='check_data',
    python_callable=check_data,
    dag=dag
)

end_task = DummyOperator(
    task_id='end_task',
    trigger_rule='all_done',
    dag=dag
)

create_table >> load_data_task >> check_data_task >> end_task