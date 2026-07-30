from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.operators.emr import EmrAddStepsOperator
from airflow.providers.amazon.aws.sensors.emr import EmrStepSensor
import logging

default_args = {
    'owner': 'urn:li:corpuser:jdoe, urn:li:corpuser:datahub',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

def create_fct_users_created(**kwargs):
    """
    Creates fct_users_created table by querying logging_events table.
    """
    try:
        # Initialize Spark session
        from pyspark.sql import SparkSession
        spark = SparkSession.builder.getOrCreate()

        # Read logging_events table
        logging_events_df = spark.read.format('parquet').load('s3://logging-events-prod')

        # Create fct_users_created table
        fct_users_created_df = logging_events_df.select(
            logging_events_df.user_id.cast('string').alias('user_id'),
            logging_events_df.user_name.cast('boolean').alias('user_name')
        ).dropDuplicates()

        # Write fct_users_created table to S3
        fct_users_created_df.write.format('parquet').mode('overwrite').save('s3://fct-users-created-prod')

        spark.stop()

        logging.info('fct_users_created table created successfully')

    except Exception as e:
        logging.error(f'Error creating fct_users_created table: {e}')
        raise

with DAG(
    'fct_users_created_dag',
    default_args=default_args,
    description='Creates fct_users_created table',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    tags=[],
) as dag:
    create_fct_users_created_task = PythonOperator(
        task_id='create_fct_users_created',
        python_callable=create_fct_users_created,
    )

    end_task = DummyOperator(
        task_id='end_task',
        trigger_rule='all_done',
    )

    create_fct_users_created_task >> end_task