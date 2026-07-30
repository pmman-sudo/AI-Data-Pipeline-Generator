from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.operators.emr import EMROperator
from airflow.providers.amazon.aws.sensors.emr import EMRJobFlowSensor
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'fct_users_created_dag',
    default_args=default_args,
    description='DAG to create fct_users_created table',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(1),
    tags=['fct_users_created']
)

def create_fct_users_created_table(**kwargs):
    """
    Create fct_users_created table.
    """
    from pyspark.sql import SparkSession
    spark = SparkSession.builder.getOrCreate()
    spark.sql("CREATE TABLE IF NOT EXISTS fct_users_created (user_id varchar(100), user_name boolean)")
    spark.stop()

create_fct_users_created_task = PythonOperator(
    task_id='create_fct_users_created_task',
    python_callable=create_fct_users_created_table,
    dag=dag
)

create_fct_users_created_task

def load_data_into_fct_users_created_table(**kwargs):
    """
    Load data into fct_users_created table.
    """
    from pyspark.sql import SparkSession
    spark = SparkSession.builder.getOrCreate()
    df = spark.read.table("logging_events")
    df = df.select("user_id", "user_name")
    df.write.format("parquet").mode("overwrite").saveAsTable("fct_users_created")
    spark.stop()

load_data_into_fct_users_created_task = PythonOperator(
    task_id='load_data_into_fct_users_created_task',
    python_callable=load_data_into_fct_users_created_table,
    dag=dag
)

create_fct_users_created_task >> load_data_into_fct_users_created_task

def check_fct_users_created_table(**kwargs):
    """
    Check fct_users_created table.
    """
    from pyspark.sql import SparkSession
    spark = SparkSession.builder.getOrCreate()
    df = spark.table("fct_users_created")
    if df.count() == 0:
        raise ValueError("fct_users_created table is empty")
    spark.stop()

check_fct_users_created_task = PythonOperator(
    task_id='check_fct_users_created_task',
    python_callable=check_fct_users_created_table,
    dag=dag
)

load_data_into_fct_users_created_task >> check_fct_users_created_task