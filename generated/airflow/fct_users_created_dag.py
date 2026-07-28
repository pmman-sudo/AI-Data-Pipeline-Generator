from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.providers.amazon.aws.operators.redshift import RedshiftOperator
from airflow.utils.db import provide_session
from airflow.hooks.base import BaseHook
import logging

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 12, 1),
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,
}

def load_data(**kwargs):
    """
    Load data from logging_events into fct_users_created table.
    
    :param kwargs: Airflow context
    """
    try:
        # Get Redshift connection
        redshift_conn = BaseHook.get_connection('redshift')
        
        # Create SQL query
        sql = """
            INSERT INTO fct_users_created (user_id, user_name)
            SELECT DISTINCT user_id, user_name
            FROM logging_events
            WHERE user_name IS NOT NULL;
        """
        
        # Create Redshift operator
        redshift_op = RedshiftOperator(
            task_id='load_data',
            conn_id='redshift',
            sql=sql,
            params=kwargs
        )
        
        # Execute Redshift operator
        redshift_op.execute(context=kwargs)
        
        logging.info('Data loaded into fct_users_created table')
    except Exception as e:
        logging.error(f'Error loading data: {str(e)}')
        raise

dag = DAG(
    'fct_users_created_dag',
    default_args=default_args,
    description='Load data from logging_events into fct_users_created table',
    schedule_interval=timedelta(days=1),
)

load_data_task = PythonOperator(
    task_id='load_data',
    python_callable=load_data,
    dag=dag
)