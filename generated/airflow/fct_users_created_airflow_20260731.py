from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.transfers.hive import HiveOperator
from airflow.utils.dates import days_ago
import json
import logging

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
    Creates the fct_users_created table by querying the logging_events table.

    :param kwargs:
    :return:
    """
    logging.info('Creating fct_users_created table')
    hive_query = """
        CREATE TABLE IF NOT EXISTS fct_users_created (
            user_id VARCHAR(100),
            user_name BOOLEAN
        );
        
        INSERT INTO fct_users_created
        SELECT 
            user_id,
            user_name
        FROM 
            logging_events;
    """
    HiveOperator(
        task_id='create_fct_users_created',
        hql=hive_query,
        hive_cli_conn_id='hive_default',
        dag=dag
    )

dag = DAG(
    'fct_users_created_dag',
    default_args=default_args,
    description='A DAG to create the fct_users_created table',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(1),
    tags=[],
    catchup=False,
)

create_fct_users_created_task = PythonOperator(
    task_id='create_fct_users_created_task',
    python_callable=create_fct_users_created,
    dag=dag
)

end_task = DummyOperator(
    task_id='end_task',
    trigger_rule='all_done',
    dag=dag
)

create_fct_users_created_task >> end_task