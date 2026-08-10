from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
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

def load_data(**kwargs):
    postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
    conn = postgres_hook.get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM fct_users_created")
    rows = cur.fetchall()
    return rows

def transform_data(**kwargs):
    rows = kwargs['ti'].xcom_pull(task_ids='load_data')
    transformed_rows = []
    for row in rows:
        transformed_row = {
            'user_id': row[0],
            'created_at': row[1],
            'email': row[2],
        }
        transformed_rows.append(transformed_row)
    return transformed_rows

def validate_data(**kwargs):
    rows = kwargs['ti'].xcom_pull(task_ids='transform_data')
    for row in rows:
        if not row['user_id'] or not row['created_at'] or not row['email']:
            raise ValueError("Invalid data")

with DAG(
    'fct_users_created_dag',
    default_args=default_args,
    description='A DAG to load, transform, and validate fct_users_created data',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2022, 1, 1),
    tags=['Demo'],
) as dag:
    load_data_task = PythonOperator(
        task_id='load_data',
        python_callable=load_data,
    )

    transform_data_task = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data,
    )

    validate_data_task = PythonOperator(
        task_id='validate_data',
        python_callable=validate_data,
    )

    load_data_task >> transform_data_task >> validate_data_task

def validate_dag(dag):
    try:
        dag.run_test()
        return "DAG is valid"
    except Exception as e:
        return str(e)

print(validate_dag(dag))

# simulate git commit
git_commit_message = "Created fct_users_created DAG"
print(f"Committed to GitHub: {git_commit_message}")