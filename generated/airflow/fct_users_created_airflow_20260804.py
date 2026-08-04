from datetime import datetime, timedelta
from airflow import DAG
from airflow.decorators import task
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from airflow.providers.snowflake.transfers.postgres_to_snowflake import PostgresToSnowflakeOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from airflow.hooks.base import BaseHook
from airflow.exceptions import AirflowException
import logging

default_args = {
    'owner': 'Demo',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

@task
def validate_schema():
    """
    Validate schema of customer_orders table in PostgreSQL database.
    """
    pg_hook = PostgresHook(postgres_conn_id='postgres_default')
    conn = pg_hook.get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'customer_orders'")
    columns = cursor.fetchall()
    expected_columns = [('user_id', 'bigint'), ('created_at', 'timestamp without time zone'), ('email', 'character varying')]
    if set(columns) != set(expected_columns):
        raise AirflowException('Schema validation failed')
    return True

@task
def extract_data(**kwargs):
    """
    Extract customer_orders table from PostgreSQL database incrementally using updated_at.
    """
    pg_hook = PostgresHook(postgres_conn_id='postgres_default')
    conn = pg_hook.get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customer_orders WHERE updated_at > (NOW() - INTERVAL '1 day')")
    data = cursor.fetchall()
    return data

@task
def perform_quality_checks(data):
    """
    Perform data quality checks (null values, duplicates, row count).
    """
    if not data:
        raise AirflowException('No data found')
    for row in data:
        if None in row:
            raise AirflowException('Null value found')
    if len(data) != len(set(data)):
        raise AirflowException('Duplicates found')
    return True

@task
def load_data(**kwargs):
    """
    Load transformed data into Snowflake.
    """
    sf_hook = SnowflakeHook(snowflake_conn_id='snowflake_default')
    conn = sf_hook.get_conn()
    cursor = conn.cursor()
    data = kwargs['ti'].xcom_pull(task_ids='extract_data')
    for row in data:
        cursor.execute("INSERT INTO fct_users_created (user_id, created_at, email) VALUES (%s, %s, %s)", row)
    conn.commit()
    return True

@task
def trigger_dbt_models(**kwargs):
    """
    Trigger dbt models after successful load.
    """
    bash_cmd = "dbt run --m fct_users_created"
    bash_operator = BashOperator(
        task_id='trigger_dbt_models',
        bash_command=bash_cmd,
    )
    return bash_operator.execute(kwargs['context'])

@task
def update_datahub_metadata(**kwargs):
    """
    Update DataHub metadata after pipeline completion.
    """
    # implement datahub metadata update logic here
    return True

@task
def send_slack_notification(**kwargs):
    """
    Send Slack notification on success or failure.
    """
    # implement slack notification logic here
    return True

with DAG(
    'customer_orders_pipeline',
    default_args=default_args,
    description='A DAG to extract customer orders data from PostgreSQL and load it into Snowflake',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(1),
    tags=['Demo'],
) as dag:
    validate_schema_task = validate_schema()
    extract_data_task = extract_data()
    quality_checks_task = perform_quality_checks(extract_data_task)
    load_data_task = load_data()
    trigger_dbt_models_task = trigger_dbt_models()
    update_datahub_metadata_task = update_datahub_metadata()
    send_slack_notification_task = send_slack_notification()

    validate_schema_task >> extract_data_task >> quality_checks_task >> load_data_task >> trigger_dbt_models_task >> update_datahub_metadata_task >> send_slack_notification_task