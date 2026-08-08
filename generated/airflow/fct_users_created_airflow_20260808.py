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

def load_fct_users_created():
    # TO DO: Load data into fct_users_created table
    pass

def validate_fct_users_created():
    # TO DO: Validate data in fct_users_created table
    pass

with DAG(
    'fct_users_created_dag',
    default_args=default_args,
    description='A DAG to manage the fct_users_created table',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 12, 1),
    tags=[],
) as dag:
    load_data = PythonOperator(
        task_id='load_fct_users_created',
        python_callable=load_fct_users_created,
    )

    validate_data = PythonOperator(
        task_id='validate_fct_users_created',
        python_callable=validate_fct_users_created,
    )

    load_data >> validate_data