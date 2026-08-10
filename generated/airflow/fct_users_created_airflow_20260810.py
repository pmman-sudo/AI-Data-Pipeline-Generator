from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

default_args = {
    'owner': 'Demo',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def validate_data(**kwargs):
    # Validate the data
    print("Validating data...")

def load_data(**kwargs):
    # Load the data
    print("Loading data...")

def transform_data(**kwargs):
    # Transform the data
    print("Transforming data...")

with DAG(
    'fct_users_created_dag',
    default_args=default_args,
    description='A DAG to load, transform, and validate the fct_users_created table',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2022, 1, 1),
    tags=['Demo'],
) as dag:
    start = EmptyOperator(
        task_id='start',
    )

    load = BashOperator(
        task_id='load_data',
        bash_command='echo "Loading data..."',
    )

    transform = BashOperator(
        task_id='transform_data',
        bash_command='echo "Transforming data..."',
    )

    validate = PythonOperator(
        task_id='validate_data',
        python_callable=validate_data,
    )

    spark_task = SparkSubmitOperator(
        task_id='spark_task',
        conn_id='spark_default',
        application='/path/to/your/spark/application.py',
        jars=['/path/to/your/jar1.jar', '/path/to/your/jar2.jar'],
        application_args=['arg1', 'arg2'],
        driver_classpath=['/path/to/your/driver/classpath'],
        spark_binary='/path/to/your/spark/binary',
        conf={'key': 'value'},
        verbose=True,
    )

    end = EmptyOperator(
        task_id='end',
    )

    start >> load >> transform >> validate >> spark_task >> end