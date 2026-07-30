from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.operators.s3 import S3KeySensor
from airflow.providers.amazon.aws.transfers.s3 import S3Key
import logging

default_args = {
    'owner': 'urn:li:corpuser:jdoe, urn:li:corpuser:datahub',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

def fetch_data(**kwargs):
    """
    Fetches data from the logging_events table in Hive and creates a fact table fct_users_created.
    
    :param kwargs: Keyword arguments
    :return: None
    """
    try:
        # Import necessary libraries
        from pyspark.sql import SparkSession
        from pyspark.sql.functions import col

        # Create a Spark session
        spark = SparkSession.builder.appName('fct_users_created').getOrCreate()

        # Read data from logging_events table
        logging_events_df = spark.read.format('hive').load('logging_events')

        # Create fct_users_created fact table
        fct_users_created_df = logging_events_df.select(
            col('user_id').cast('string'),
            col('user_name').cast('boolean')
        )

        # Write data to fct_users_created table
        fct_users_created_df.write.format('hive').saveAsTable('fct_users_created')

        # Stop the Spark session
        spark.stop()

        logging.info('Data fetched and fct_users_created table created successfully')

    except Exception as e:
        logging.error('Error fetching data: %s', e)

with DAG(
    'fct_users_created_dag',
    default_args=default_args,
    description='A DAG to create fct_users_created fact table',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:
    fetch_data_task = PythonOperator(
        task_id='fetch_data',
        python_callable=fetch_data
    )