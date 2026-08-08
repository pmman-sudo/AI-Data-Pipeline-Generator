from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'Paul',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'fct_users_created_dag',
    default_args=default_args,
    description='DAG for fct_users_created table',
    schedule_interval=None,
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=[],
) as dag:
    start_task = DummyOperator(
        task_id='start_task',
    )

    create_fct_users_created_table = BashOperator(
        task_id='create_fct_users_created_table',
        bash_command='echo "Create fct_users_created table"'
    )

    load_fct_users_created_data = BashOperator(
        task_id='load_fct_users_created_data',
        bash_command='echo "Load data into fct_users_created table"'
    )

    end_task = DummyOperator(
        task_id='end_task',
    )

    start_task >> create_fct_users_created_table >> load_fct_users_created_data >> end_task