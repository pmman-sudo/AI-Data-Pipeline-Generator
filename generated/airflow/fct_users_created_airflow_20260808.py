from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'Paul',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

def create_fct_users_created(**kwargs):
    # TO DO: implement data creation logic for fct_users_created table
    pass

with DAG(
    'fct_users_created_dag',
    default_args=default_args,
    description='A DAG for creating the fct_users_created table',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 12, 1),
    tags=[]
) as dag:
    start_task = DummyOperator(
        task_id='start_task'
    )

    create_fct_users_created_task = PythonOperator(
        task_id='create_fct_users_created',
        python_callable=create_fct_users_created
    )

    end_task = DummyOperator(
        task_id='end_task'
    )

    start_task >> create_fct_users_created_task >> end_task