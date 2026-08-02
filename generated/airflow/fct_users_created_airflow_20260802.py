from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.log import LoggingMixin
from structlog import get_logger

LOG = get_logger()

default_args = {
    'owner': 'Demo',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,
}

def create_fct_users_created(**kwargs):
    """
    Create fct_users_created table
    """
    try:
        # Create the table
        # Replace with actual database connection
        import pandas as pd
        data = {'user_id': [1], 'created_at': [datetime.now()], 'email': ['example@example.com']}
        df = pd.DataFrame(data)
        # Save to database
        # Replace with actual database connection
        LOG.info('fct_users_created table created')
    except Exception as e:
        LOG.error(f'Failed to create fct_users_created table: {e}')
        raise

def load_fct_users_created(**kwargs):
    """
    Load data into fct_users_created table
    """
    try:
        # Load data from source
        # Replace with actual data source
        data = {'user_id': [1], 'created_at': [datetime.now()], 'email': ['example@example.com']}
        # Save to database
        # Replace with actual database connection
        LOG.info('fct_users_created table loaded')
    except Exception as e:
        LOG.error(f'Failed to load fct_users_created table: {e}')
        raise

with DAG(
    'fct_users_created_dag',
    default_args=default_args,
    description='A DAG to create and load fct_users_created table',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    tags=['Demo'],
) as dag:
    create_fct_users_created_task = PythonOperator(
        task_id='create_fct_users_created',
        python_callable=create_fct_users_created,
    )
    load_fct_users_created_task = PythonOperator(
        task_id='load_fct_users_created',
        python_callable=load_fct_users_created,
    )
    create_fct_users_created_task >> load_fct_users_created_task