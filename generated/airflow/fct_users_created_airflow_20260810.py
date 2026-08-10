from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.bash import BashOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.sensors.postgres import PostgresSensor

default_args = {
    'owner': 'Demo',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'fct_users_created_pipeline',
    default_args=default_args,
    description='Pipeline for fct_users_created table',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    tags=['Demo'],
) as dag:

    start_task = DummyOperator(
        task_id='start_task',
    )

    check_table_exists = PostgresSensor(
        task_id='check_table_exists',
        conn_id='postgres_conn',
        sql='SELECT EXISTS(SELECT 1 FROM pg_tables WHERE tablename = \'fct_users_created\')',
        timeout=18*60*60,  # 18 hours
        poke_interval=60,  # 1 minute
    )

    create_table = PostgresOperator(
        task_id='create_table',
        conn_id='postgres_conn',
        sql='''
            CREATE TABLE IF NOT EXISTS fct_users_created (
                user_id BIGINT PRIMARY KEY,
                created_at TIMESTAMP,
                email STRING
            );
        ''',
    )

    insert_data = PostgresOperator(
        task_id='insert_data',
        conn_id='postgres_conn',
        sql='''
            INSERT INTO fct_users_created (user_id, created_at, email)
            VALUES (1, NOW(), 'example@example.com');
        ''',
    )

    end_task = DummyOperator(
        task_id='end_task',
    )

    start_task >> check_table_exists >> create_table >> insert_data >> end_task