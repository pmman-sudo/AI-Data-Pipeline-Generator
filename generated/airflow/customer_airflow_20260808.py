from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.operators.aws_cloudwatch_logs import CloudWatchLogHook
import logging

default_args = {
    'owner': 'Demo',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

def extract_customer_data(**kwargs):
    try:
        # Simulate data extraction from customer table
        customer_data = [
            {'user_id': 1, 'created_at': datetime(2022, 1, 1), 'email': 'user1@example.com'},
            {'user_id': 2, 'created_at': datetime(2022, 1, 15), 'email': 'user2@example.com'}
        ]
        logging.info(f"Extracted customer data: {customer_data}")
        return customer_data
    except Exception as e:
        logging.error(f"Error extracting customer data: {str(e)}")
        raise

def process_customer_data(**kwargs):
    task_instance = kwargs['task_instance']
    customer_data = task_instance.xcom_pull(task_ids='extract_customer_data')
    try:
        # Simulate data processing
        processed_data = [{'user_id': item['user_id'], 'created_at': item['created_at'], 'email': item['email']} for item in customer_data]
        logging.info(f"Processed customer data: {processed_data}")
        return processed_data
    except Exception as e:
        logging.error(f"Error processing customer data: {str(e)}")
        raise

def load_customer_data(**kwargs):
    task_instance = kwargs['task_instance']
    customer_data = task_instance.xcom_pull(task_ids='process_customer_data')
    try:
        # Simulate data loading
        logging.info(f"Loaded customer data: {customer_data}")
    except Exception as e:
        logging.error(f"Error loading customer data: {str(e)}")
        raise

dag = DAG(
    'customer_orders_dag',
    default_args=default_args,
    description='A DAG to extract, process, and load customer order data',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2022, 1, 1),
    tags=['Demo']
)

extract_customer_data_task = PythonOperator(
    task_id='extract_customer_data',
    python_callable=extract_customer_data,
    dag=dag
)

process_customer_data_task = PythonOperator(
    task_id='process_customer_data',
    python_callable=process_customer_data,
    dag=dag
)

load_customer_data_task = PythonOperator(
    task_id='load_customer_data',
    python_callable=load_customer_data,
    dag=dag
)

end_task = DummyOperator(
    task_id='end_task',
    trigger_rule='all_done',
    dag=dag
)

extract_customer_data_task >> process_customer_data_task >> load_customer_data_task >> end_task