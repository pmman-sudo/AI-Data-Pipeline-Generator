from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator

default_args = {
    'owner': 'Paul',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def check_table_exists(**kwargs):
    import pandas as pd
    from sqlalchemy import create_engine
    engine = create_engine('postgresql://user:password@host:port/dbname')
    query = "SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name='fct_users_created');"
    result = pd.read_sql_query(query, engine)
    if result.iloc[0][0]:
        return True
    else:
        raise ValueError("Table fct_users_created does not exist")

def load_data(**kwargs):
    from sqlalchemy import create_engine
    engine = create_engine('postgresql://user:password@host:port/dbname')
    query = "INSERT INTO fct_users_created (id) SELECT id FROM src_users;"
    engine.execute(query)

with DAG(
    'fct_users_created_dag',
    default_args=default_args,
    description='A DAG for the fct_users_created table',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=[],
) as dag:
    check_table = PythonOperator(
        task_id='check_table',
        python_callable=check_table_exists,
    )
    load_data_task = PythonOperator(
        task_id='load_data',
        python_callable=load_data,
    )
    check_table >> load_data_task