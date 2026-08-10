from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

default_args = {
    'owner': 'Demo',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def validate_data(**kwargs):
    pg_hook = PostgresHook(postgres_conn_id='postgres_default')
    conn = pg_hook.get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM fct_users_created WHERE created_at IS NULL OR email IS NULL")
    invalid_rows = cur.fetchall()
    if len(invalid_rows) > 0:
        raise ValueError("Invalid data found in fct_users_created table")
    conn.close()

def load_data(**kwargs):
    pg_hook = PostgresHook(postgres_conn_id='postgres_default')
    conn = pg_hook.get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM src_users")
    rows = cur.fetchall()
    insert_stmt = "INSERT INTO fct_users_created (user_id, created_at, email) VALUES (%s, %s, %s)"
    for row in rows:
        cur.execute(insert_stmt, row)
    conn.commit()
    conn.close()

def transform_data(**kwargs):
    pg_hook = PostgresHook(postgres_conn_id='postgres_default')
    conn = pg_hook.get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE fct_users_created SET created_at = NOW() WHERE created_at IS NULL")
    conn.commit()
    conn.close()

dag = DAG(
    'fct_users_created_dag',
    default_args=default_args,
    description='A DAG for loading and transforming fct_users_created table',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    tags=['Demo'],
)

load_task = PostgresOperator(
    task_id='load_data',
    dag=dag,
    conn_id='postgres_default',
    sql="TRUNCATE fct_users_created; INSERT INTO fct_users_created (user_id, created_at, email) SELECT user_id, created_at, email FROM src_users",
)

transform_task = PythonOperator(
    task_id='transform_data',
    dag=dag,
    python_callable=transform_data,
)

validate_task = PythonOperator(
    task_id='validate_data',
    dag=dag,
    python_callable=validate_data,
)

commit_task = BashOperator(
    task_id='commit_code',
    dag=dag,
    bash_command='git add . && git commit -m "Updated fct_users_created_dag" && git push origin main',
)

load_task >> transform_task >> validate_task >> commit_task