from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator

default_args = {
    'owner': 'Paul',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def load_data(**kwargs):
    # Load data into fct_users_created table
    # Replace this function with actual data loading logic
    pass

def transform_data(**kwargs):
    # Transform data in fct_users_created table
    # Replace this function with actual data transformation logic
    pass

def validate_data(**kwargs):
    # Validate data in fct_users_created table
    # Replace this function with actual data validation logic
    pass

dag = DAG(
    'fct_users_created_dag',
    default_args=default_args,
    description='A DAG for the fct_users_created table',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    tags=[],
)

load_data_task = PythonOperator(
    task_id='load_data',
    python_callable=load_data,
    dag=dag,
)

transform_data_task = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    dag=dag,
)

validate_data_task = PythonOperator(
    task_id='validate_data',
    python_callable=validate_data,
    dag=dag,
)

load_data_task >> transform_data_task >> validate_data_task