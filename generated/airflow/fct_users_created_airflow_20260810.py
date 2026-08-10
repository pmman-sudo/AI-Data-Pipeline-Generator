from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    "owner": "Paul",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

def load_data():
    pass

def transform_data():
    pass

def validate_data():
    pass

with DAG(
    "fct_users_created_dag",
    default_args=default_args,
    description="DAG for fct_users_created",
    schedule=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=[],
) as dag:

    load_task = PythonOperator(
        task_id="load_data",
        python_callable=load_data,
    )

    transform_task = PythonOperator(
        task_id="transform_data",
        python_callable=transform_data,
    )

    validate_task = PythonOperator(
        task_id="validate_data",
        python_callable=validate_data,
    )

    load_task >> transform_task >> validate_task