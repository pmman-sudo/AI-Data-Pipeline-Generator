from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.transfers.hive import HiveOperator
from airflow.utils.dates import days_ago
import logging

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

def create_fct_users_created(**kwargs):
    """
    Create fct_users_created table.
    
    :param kwargs: Keyword arguments
    :return: None
    """
    try:
        # Define the Hive query to create the table
        hive_query = """
            CREATE TABLE IF NOT EXISTS fct_users_created (
                user_id VARCHAR(100),
                user_name BOOLEAN
            );
        """
        
        # execute the query
        HiveOperator(
            task_id='create_fct_users_created',
            hive_cli_conn_id='hive_default',
            hive_query=hive_query,
            retry_args=default_args
        ).execute(kwargs)
        
        logging.info("Table fct_users_created created successfully")
        
    except Exception as e:
        logging.error(f"Error creating table fct_users_created: {str(e)}")

def load_fct_users_created(**kwargs):
    """
    Load data into fct_users_created table.
    
    :param kwargs: Keyword arguments
    :return: None
    """
    try:
        # Define the Hive query to load data into the table
        hive_query = """
            INSERT INTO fct_users_created
            SELECT 
                user_id,
                user_name
            FROM logging_events;
        """
        
        # execute the query
        HiveOperator(
            task_id='load_fct_users_created',
            hive_cli_conn_id='hive_default',
            hive_query=hive_query,
            retry_args=default_args
        ).execute(kwargs)
        
        logging.info("Data loaded into fct_users_created successfully")
        
    except Exception as e:
        logging.error(f"Error loading data into fct_users_created: {str(e)}")

with DAG(
    'fct_users_created_dag',
    default_args=default_args,
    description='A DAG to create and load fct_users_created table',
    schedule_interval=None,
    start_date=days_ago(1),
    tags=['data_warehouse'],
    catchup=False,
) as dag:
    create_table-task = PythonOperator(
        task_id='create_fct_users_created',
        python_callable=create_fct_users_created
    )
    
    load_data_task = PythonOperator(
        task_id='load_fct_users_created',
        python_callable=load_fct_users_created
    )
    
    create_table-task >> load_data_task