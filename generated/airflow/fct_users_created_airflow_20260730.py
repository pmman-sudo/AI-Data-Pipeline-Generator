from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
import logging

default_args = {
    'owner': 'urn:li:corpuser:jdoe, urn:li:corpuser:datahub',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5)
}

def create_fct_users_created(**kwargs):
    try:
        logging.info('Creating fct_users_created table')
        # Simulate creation of fct_users_created table
        logging.info('fct_users_created table created successfully')
    except Exception as e:
        logging.error('Error creating fct_users_created table: %s', e)
        raise

def load_fct_users_created(**kwargs):
    try:
        logging.info('Loading data into fct_users_created table')
        # Simulate loading data into fct_users_created table
        logging.info('Data loaded into fct_users_created table successfully')
    except Exception as e:
        logging.error('Error loading data into fct_users_created table: %s', e)
        raise

with DAG(
    'fct_users_created_dag',
    default_args=default_args,
    description='A DAG to create and load fct_users_created table',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(1)
) as dag:
    create_table_task = PythonOperator(
        task_id='create_table',
        python_callable=create_fct_users_created
    )

    load_data_task = PythonOperator(
        task_id='load_data',
        python_callable=load_fct_users_created
    )

    end_task = BashOperator(
        task_id='end_task',
        bash_command='echo "DAG completed Successfully"'
    )

    create_table_task >> load_data_task >> end_task