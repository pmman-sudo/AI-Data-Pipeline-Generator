"""
This DAG is used to manage the fct_users_created table.
It includes tasks to handle user creation and provides
structured logging, explicit error handling, and retries with exponential backoff.

"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from airflow.utils.log.logging_mixin import LoggingMixin
from datetime import datetime, timedelta

# Define constants for exponential backoff
RETRIES = 3
RETRY_DELAY = timedelta(seconds=10)
DEFAULT_ARGS = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': RETRIES,
    'retry_delay': RETRY_DELAY,
}

def create_user(**kwargs):
    """
    Task to create a new user in the fct_users_created table.
    
    :param kwargs: Airflow task context
    :return: None
    """
    try:
        # Here you should implement the logic to create a new user
        # This is a placeholder function and does not create a user in the actual database
        LoggingMixin().log.info('Creating user with id: %s and name: %s', kwargs['user_id'], kwargs['user_name'])
    except Exception as e:
        LoggingMixin().log.error('Error creating user: %s', str(e))
        raise

def get_user(**kwargs):
    """
    Task to get a user from the fct_users_created table.
    
    :param kwargs: Airflow task context
    :return: None
    """
    try:
        # Here you should implement the logic to get a user
        # This is a placeholder function and does not get a user from the actual database
        LoggingMixin().log.info('Getting user with id: %s', kwargs['user_id'])
    except Exception as e:
        LoggingMixin().log.error('Error getting user: %s', str(e))
        raise

with DAG(
    'fct_users_created_dag',
    default_args=DEFAULT_ARGS,
    description='A DAG to manage fct_users_created table',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(1),
    catchup=False,
) as dag:
    create_user_task = PythonOperator(
        task_id='create_user_task',
        python_callable=create_user,
        op_kwargs={'user_id': 'user123', 'user_name': True}
    )
    get_user_task = PythonOperator(
        task_id='get_user_task',
        python_callable=get_user,
        op_kwargs={'user_id': 'user123'}
    )
    end_task = DummyOperator(
        task_id='end_task',
    )
    create_user_task >> get_user_task >> end_task