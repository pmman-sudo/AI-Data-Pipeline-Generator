from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.transfers.hive import HiveOperator
from airflow.utils.db import provide_session
from airflow.utils.log import LoggingMixin
from airflow.models import Variable

default_args = {
    'owner': 'jdoe',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True
}

def create_fct_users_created(**kwargs):
    """
    Create the fct_users_created table.
    
    :param kwargs: Airflow context
    :return: None
    """
    hive Conn = HiveOperator(
        task_id='create_fct_users_created',
        hive_cli_conn_id='hive_default',
        sql=f"""
            CREATE TABLE IF NOT EXISTS fct_users_created (
                user_id varchar(100),
                user_name boolean
            );
        """
    )
    return hive_conn.execute(f"""
            CREATE TABLE IF NOT EXISTS fct_users_created (
                user_id varchar(100),
                user_name boolean
            );
        """)

def populate_fct_users_created(**kwargs):
    """
    Populate the fct_users_created table.
    
    :param kwargs: Airflow context
    :return: None
    """
    hive_conn = HiveOperator(
        task_id='populate_fct_users_created',
        hive_cli_conn_id='hive_default',
        sql=f"""
            INSERT INTO fct_users_created
            SELECT 
                user_id,
                user_name
            FROM logging_events;
        """
    )
    return hive_conn.execute(f"""
            INSERT INTO fct_users_created
            SELECT 
                user_id,
                user_name
            FROM logging_events;
        """)

with DAG(
    'fct_users_created_dag',
    default_args=default_args,
    description='A DAG to create and populate the fct_users_created table',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 12, 1),
    catchup=False,
    tags=['fct_users_created']
) as dag:
    create_table = PythonOperator(
        task_id='create_fct_users_created',
        python_callable=create_fct_users_created
    )
    populate_table = PythonOperator(
        task_id='populate_fct_users_created',
        python_callable=populate_fct_users_created
    )
    
    create_table >> populate_table