from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
import logging

default_args = {
    'owner': 'Demo',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2024, 1, 1)
}

def create_fct_users_created(**kwargs):
    try:
        # Create fct_users_created table
        logging.info('Creating fct_users_created table')
        # Add your SQL query or function to create the table here
        logging.info('fct_users_created table creation successful')
    except Exception as e:
        logging.error(f'Error creating fct_users_created table: {e}')

def populate_fct_users_created(**kwargs):
    try:
        # Populate fct_users_created table
        logging.info('Populating fct_users_created table')
        # Add your SQL query or function to populate the table here
        logging.info('fct_users_created table population successful')
    except Exception as e:
        logging.error(f'Error populating fct_users_created table: {e}')

dag = DAG(
    'fct_users_created_dag',
    default_args=default_args,
    schedule_interval='@daily',
    tags=['Demo']
)

create_fct_users_created_task = PythonOperator(
    task_id='create_fct_users_created',
    python_callable=create_fct_users_created,
    dag=dag
)

populate_fct_users_created_task = PythonOperator(
    task_id='populate_fct_users_created',
    python_callable=populate_fct_users_created,
    dag=dag
)

end_task = BashOperator(
    task_id='end_task',
    bash_command='echo "fct_users_created dag completed"',
    dag=dag
)

create_fct_users_created_task >> populate_fct_users_created_task >> end_task