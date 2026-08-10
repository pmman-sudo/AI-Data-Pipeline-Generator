from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.providers.amazon.aws.operators.redshift import RedshiftRunQueryOperator

default_args = {
    'owner': 'Demo',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'fct_users_created_dag',
    default_args=default_args,
    description='DAG for fct_users_created table',
    schedule_interval='@daily',
    start_date=datetime(2023, 12, 1),
    tags=['Demo'],
)

start_task = DummyOperator(
    task_id='start_task',
    dag=dag,
)

end_task = DummyOperator(
    task_id='end_task',
    dag=dag,
)

create_table_task = RedshiftRunQueryOperator(
    task_id='create_table',
    query="""
        CREATE TABLE IF NOT EXISTS fct_users_created (
            user_id BIGINT,
            created_at TIMESTAMP,
            email VARCHAR(255)
        );
    """,
    dag=dag,
)

insert_data_task = RedshiftRunQueryOperator(
    task_id='insert_data',
    query="""
        INSERT INTO fct_users_created (user_id, created_at, email)
        SELECT user_id, created_at, email
        FROM src_users;
    """,
    dag=dag,
)

start_task >> create_table_task >> insert_data_task >> end_task