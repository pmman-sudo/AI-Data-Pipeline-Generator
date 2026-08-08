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
    description='A DAG for the fct_users_created table',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 12, 1),
    tags=[],
) as dag:
    start_task = DummyOperator(
        task_id='start_task',
    )

    end_task = DummyOperator(
        task_id='end_task',
    )

    create_fct_users_created_table = BashOperator(
        task_id='create_fct_users_created_table',
        bash_command='''
            echo "Creating fct_users_created table"
            # Add SQL command to create table here
        ''',
    )

    populate_fct_users_created_table = BashOperator(
        task_id='populate_fct_users_created_table',
        bash_command='''
            echo "Populating fct_users_created table"
            # Add SQL command to populate table here
        ''',
    )

    start_task >> create_fct_users_created_table >> populate_fct_users_created_table >> end_task