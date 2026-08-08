from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.operators.redshift import RedshiftSQLOperator
import logging

default_args = {
    'owner': 'Demo',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

def load_customer_orders(**kwargs):
    """Loads customer orders into Redshift"""
    try:
        logging.info('Loading customer orders')
        # TO DO: implement the logic to load customer orders
    except Exception as e:
        logging.error(f'Failed to load customer orders: {str(e)}')
        raise

dag = DAG(
    'customer_orders_dag',
    default_args=default_args,
    description='A DAG to load customer orders',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 12, 1),
    tags=['Demo'],
)

load_customer_orders_task = PythonOperator(
    task_id='load_customer_orders',
    python_callable=load_customer_orders,
    dag=dag,
)

create_customer_orders_table = RedshiftSQLOperator(
    task_id='create_customer_orders_table',
    sql='''
        CREATE TABLE IF NOT EXISTS customer_orders (
            user_id BIGINT,
            created_at TIMESTAMP,
            email STRING
        );
    ''',
    dag=dag,
)

end_task = DummyOperator(
    task_id='end_task',
    trigger_rule='all_done',
    dag=dag,
)

create_customer_orders_table >> load_customer_orders_task >> end_task