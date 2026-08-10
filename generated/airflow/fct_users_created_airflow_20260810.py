from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'Demo',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def load_data(**kwargs):
    import pandas as pd
    from sqlalchemy import create_engine

    engine = create_engine('postgresql://user:password@host:port/dbname')
    query = "SELECT * FROM fct_users_created"
    df = pd.read_sql(query, engine)

    return df

def transform_data(**kwargs):
    import pandas as pd

    df = kwargs['task_instance'].xcom_pull(task_ids='load_data')
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['email'] = df['email'].str.lower()

    return df

def validate_data(**kwargs):
    import pandas as pd

    df = kwargs['task_instance'].xcom_pull(task_ids='transform_data')
    if df.empty:
        raise ValueError("Data is empty")
    if not all(df['user_id'].notna()):
        raise ValueError("User ID contains null values")
    if not all(df['created_at'].notna()):
        raise ValueError("Created at contains null values")
    if not all(df['email'].notna()):
        raise ValueError("Email contains null values")

    return True

def commit_to_github(**kwargs):
    import git
    from git import Repo

    repo = Repo()
    repo.index.add(['dags/fct_users_created_dag.py'])
    repo.index.commit('Added fct_users_created_dag.py')

with DAG(
    'fct_users_created_dag',
    default_args=default_args,
    description='A DAG for the fct_users_created table',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(1),
    tags=['Demo'],
) as dag:
    load_data_task = PythonOperator(
        task_id='load_data',
        python_callable=load_data
    )

    transform_data_task = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data
    )

    validate_data_task = PythonOperator(
        task_id='validate_data',
        python_callable=validate_data
    )

    commit_to_github_task = PythonOperator(
        task_id='commit_to_github',
        python_callable=commit_to_github
    )

    load_data_task >> transform_data_task >> validate_data_task >> commit_to_github_task