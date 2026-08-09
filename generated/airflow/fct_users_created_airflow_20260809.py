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

def load_fct_users_created(**kwargs):
    # Load fct_users_created table
    print("Loading fct_users_created table")

def transform_fct_users_created(**kwargs):
    # Transform fct_users_created table
    print("Transforming fct_users_created table")

def validate_fct_users_created(**kwargs):
    # Validate fct_users_created table
    print("Validating fct_users_created table")

with DAG(
    'fct_users_created_dag',
    default_args=default_args,
    description='fct_users_created DAG',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2022, 1, 1),
    tags=[],
) as dag:
    load_fct_users_created_task = PythonOperator(
        task_id='load_fct_users_created',
        python_callable=load_fct_users_created,
    )

    transform_fct_users_created_task = PythonOperator(
        task_id='transform_fct_users_created',
        python_callable=transform_fct_users_created,
    )

    validate_fct_users_created_task = PythonOperator(
        task_id='validate_fct_users_created',
        python_callable=validate_fct_users_created,
    )

    load_fct_users_created_task >> transform_fct_users_created_task >> validate_fct_users_created_task