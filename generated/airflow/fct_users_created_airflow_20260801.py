from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.transfers.sql import SQLTransfer
from airflow.utils.dates import days_ago
from airflow.utils.log.logging_mixin import LoggingMixin
from datetime import datetime, timedelta
import logging

default_args = {
    'owner': 'Demo',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'count_new_users',
    default_args=default_args,
    description='Count new users created each day',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(1),
    tags=['Demo'],
)

def count_new_users(**kwargs):
    """Count new users created each day"""
    try:
        logging.info("Counting new users created each day")
        query = """
            SELECT 
                DATE(created_at) AS created_date,
                COUNT(*) AS new_users
            FROM 
                fct_users_created
            GROUP BY 
                DATE(created_at)
            ORDER BY 
                created_date DESC
        """
        transfer = SQLTransfer(
            task_id='count_new_users',
            query=query,
            destination_table='new_users_count',
            database='my_database'
        )
        transfer.execute(kwargs)
        logging.info("Counting new users completed successfully")
    except Exception as e:
        logging.error(f"Error counting new users: {str(e)}")
        raise

count_new_users_task = PythonOperator(
    task_id='count_new_users_task',
    python_callable=count_new_users,
    dag=dag
)