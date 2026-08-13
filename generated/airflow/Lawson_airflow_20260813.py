from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator

default_args = {
    'owner': 'Demo',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def extract_lawson_data(**kwargs):
    # Add your data extraction logic here
    print("Extracting Lawson data")

def transform_lawson_data(**kwargs):
    # Add your data transformation logic here
    print("Transforming Lawson data")

def load_lawson_data(**kwargs):
    # Add your data loading logic here
    print("Loading Lawson data")

with DAG(
    'lawson_dag',
    default_args=default_args,
    description='Lawson DAG',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    tags=['Demo'],
) as dag:
    extract_task = PythonOperator(
        task_id='extract_lawson_data',
        python_callable=extract_lawson_data,
    )

    transform_task = PythonOperator(
        task_id='transform_lawson_data',
        python_callable=transform_lawson_data,
    )

    load_task = PythonOperator(
        task_id='load_lawson_data',
        python_callable=load_lawson_data,
    )

    extract_task >> transform_task >> load_task