from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.apache.hive.operators.hive import HiveOperator
from airflow.providers.amazon.aws.operators.aws_base import get_aws_client

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

def extract_data(**kwargs):
    client = get_aws_client('hive')
    query = """
        SELECT user_id, user_name 
        FROM logging_events
    """
    client.execute_query(query)

def load_data(**kwargs):
    client = get_aws_client('hive')
    query = """
        INSERT INTO fct_users_created (user_id, user_name)
        SELECT user_id, user_name 
        FROM logging_events
    """
    client.execute_query(query)

with DAG(
    'fct_users_created_dag',
    default_args=default_args,
    description='A DAG to extract and load data into fct_users_created table',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    catchup=False,
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