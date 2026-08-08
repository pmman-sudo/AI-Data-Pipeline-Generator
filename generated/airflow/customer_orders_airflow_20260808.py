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

def extract_data(**kwargs):
    print("Extracting data from customer_orders")

def transform_data(**kwargs):
    print("Transforming data from customer_orders")

def load_data(**kwargs):
    print("Loading data into customer_orders")

with DAG(
    'customer_orders_dag',
    default_args=default_args,
    description='A DAG for customer_orders',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    tags=['Demo'],
) as dag:
    extract = PythonOperator(
        task_id='extract_data',
        python_callable=extract_data,
    )

    transform = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data,
    )

    load = PythonOperator(
        task_id='load_data',
        python_callable=load_data,
    )

    end_task = BashOperator(
        task_id='end_task',
        bash_command='echo "DAG finished"',
    )

    extract >> transform >> load >> end_task