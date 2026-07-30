from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.log import LoggingMixin
from structlog import get_logger

logger = get_logger(__name__)

default_args = {
    'owner': 'jdoe',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True
}

def create_fct_users_created(**kwargs):
    """
    Creates the fct_users_created table and populates it with data.
    """
    try:
        # Import necessary libraries
        from pyspark.sql import SparkSession
        from pyspark.sql.functions import col

        # Create Spark Session
        spark = SparkSession.builder.appName('fct_users_created').getOrCreate()

        # Load data from upstream table
        logging_events_df = spark.read.table('logging_events')

        # Transform data
        fct_users_created_df = logging_events_df.select(
            col('user_id').cast('string').alias('user_id'),
            col('user_name').cast('boolean').alias('user_name')
        )

        # Write data to fct_users_created table
        fct_users_created_df.write.saveAsTable('fct_users_created')

        logger.info('fct_users_created table created and populated')

    except Exception as e:
        logger.error(f'Error creating fct_users_created table: {str(e)}')
        raise

with DAG(
    'fct_users_created_dag',
    default_args=default_args,
    description='Creates the fct_users_created table and populates it with data',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=[]
) as dag:
    create_fct_users_created_task = PythonOperator(
        task_id='create_fct_users_created',
        python_callable=create_fct_users_created
    )