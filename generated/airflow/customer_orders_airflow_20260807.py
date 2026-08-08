from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.bash import BashOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator

default_args = {
    'owner': 'Demo',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'customer_orders_dag',
    default_args=default_args,
    description='A DAG for customer orders',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    tags=['Demo'],
) as dag:
    start_task = DummyOperator(
        task_id='start_task',
    )

    create_table_task = PostgresOperator(
        task_id='create_table_task',
        sql='''
            CREATE TABLE IF NOT EXISTS customer_orders (
                user_id BIGINT PRIMARY KEY,
                created_at TIMESTAMP,
                email STRING
            );
        ''',
    )

    data_ingestion_task = BashOperator(
        task_id='data_ingestion_task',
        bash_command='echo "Ingesting data into customer_orders table..."',
    )

    data_processing_task = BashOperator(
        task_id='data_processing_task',
        bash_command='echo "Processing data in customer_orders table..."',
    )

    end_task = DummyOperator(
        task_id='end_task',
    )

    start_task >> create_table_task >> data_ingestion_task >> data_processing_task >> end_task