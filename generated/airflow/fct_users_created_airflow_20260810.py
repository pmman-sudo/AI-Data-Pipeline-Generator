from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator

default_args = {
    'owner': 'Demo',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def check_table():
    import psycopg2
    conn = psycopg2.connect(
        host="localhost",
        database="database",
        user="user",
        password="password"
    )
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM fct_users_created")
    result = cur.fetchone()
    print(f"Number of rows in fct_users_created: {result[0]}")
    conn.close()

with DAG(
    'fct_users_created_dag',
    default_args=default_args,
    description='A DAG to interact with the fct_users_created table',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 12, 1),
    tags=['Demo'],
) as dag:
    task1 = PostgresOperator(
        task_id='create_table_if_not_exists',
        conn_id='postgres_default',
        sql='''
            CREATE TABLE IF NOT EXISTS fct_users_created (
                user_id BIGINT PRIMARY KEY,
                created_at TIMESTAMP,
                email STRING
            )
        '''
    )

    task2 = BashOperator(
        task_id='print_table_name',
        bash_command='echo "fct_users_created"'
    )

    task3 = PythonOperator(
        task_id='check_table',
        python_callable=check_table
    )

    task1 >> task2 >> task3