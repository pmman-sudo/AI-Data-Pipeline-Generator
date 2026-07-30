from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.log import logging
from airflow.exceptions import AirflowException
import pytz

default_args = {
    'owner': 'jdoe',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,
}

def create_fct_users_created(**kwargs):
    try:
        from airflow.providers.apache.hive.operators.hive import HiveOperator
        from airflow.providers.apache.hive.transfers.hive_to_hive import HiveToHiveOperator

        hive_conn_id = 'hive_default'

        logging.info('Creating fct_users_created table')
        create_table_sql = """
            CREATE TABLE IF NOT EXISTS fct_users_created (
                user_id VARCHAR(100),
                user_name BOOLEAN
            );
        """
        hive_op = HiveOperator(
            task_id='create_fct_users_created_table',
            hive_cli_conn_id=hive_conn_id,
            sql=create_table_sql,
        )
        hive_op.execute(context=kwargs)

        logging.info('Loading data into fct_users_created table')
        load_data_sql = """
            INSERT INTO fct_users_created
            SELECT 
                user_id,
                user_name
            FROM 
                logging_events;
        """
        hive_op = HiveOperator(
            task_id='load_data_into_fct_users_created_table',
            hive_cli_conn_id=hive_conn_id,
            sql=load_data_sql,
        )
        hive_op.execute(context=kwargs)

    except AirflowException as e:
        logging.error(f'Error creating fct_users_created table: {e}')
        raise

with DAG(
    'fct_users_created_dag',
    default_args=default_args,
    description='A DAG to create fct_users_created table',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2022, 1, 1, tzinfo=pytz.UTC),
    tags=[],
) as dag:
    create_fct_users_created_task = PythonOperator(
        task_id='create_fct_users_created',
        python_callable=create_fct_users_created,
    )
    create_fct_users_created_task