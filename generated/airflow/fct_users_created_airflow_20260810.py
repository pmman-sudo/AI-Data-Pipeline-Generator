from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'Demo',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def validate_fct_users_created(**kwargs):
    from airflow.providers.postgres.operators.postgres import PostgresOperator
    from airflow.hooks.postgres_hook import PostgresHook

    pg_hook = PostgresHook(postgres_conn_id=' airflow_db')
    conn = pg_hook.get_conn()
    cursor = conn.cursor()

    cursor.execute("SELECT count(*) FROM fct_users_created")
    row_count = cursor.fetchone()[0]
    if row_count == 0:
        raise ValueError("fct_users_created table is empty")

    cursor.execute("SELECT count(*) FROM fct_users_created WHERE created_at IS NULL")
    null_count = cursor.fetchone()[0]
    if null_count > 0:
        raise ValueError("fct_users_created table contains null created_at values")

    cursor.close()
    conn.close()

def load_fct_users_created(**kwargs):
    from airflow.providers.postgres.operators.postgres import PostgresOperator

    task = PostgresOperator(
        task_id='load_fct_users_created',
        conn_id='airflow_db',
        sql='''
            INSERT INTO fct_users_created (user_id, created_at, email)
            SELECT 
                user_id,
                created_at,
                email
            FROM 
                staging_users;
        ''',
        dag=kwargs['dag']
    )
    return task.execute(kwargs['context'])

with DAG(
    'fct_users_created_dag',
    default_args=default_args,
    description='A DAG to load fct_users_created table',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(1),
    tags=['Demo'],
) as dag:

    validate_fct_users_created_task = PythonOperator(
        task_id='validate_fct_users_created',
        python_callable=validate_fct_users_created
    )

    load_fct_users_created_task = PythonOperator(
        task_id='load_fct_users_created',
        python_callable=load_fct_users_created
    )

    end_task = BashOperator(
        task_id='end_task',
        bash_command='echo "fct_users_created_dag completed"'
    )

    load_fct_users_created_task >> validate_fct_users_created_task >> end_task