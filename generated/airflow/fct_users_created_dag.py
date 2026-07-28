from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.log import logging
from airflow.utils.backoff import exponential_backoff

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_backoff_factor': 5  # Exponential backoff with 5x multiplier
}

def extract_users_created(**kwargs):
    """
    Extract user-created data from the logging_events dataset in Hive.
    """
    try:
        # Connect to Hive using the provided credentials
        # NOTE: You should replace the placeholder credentials with actual values
        # and consider using a secrets manager like AWS Secrets Manager or HashiCorp Vault
        hive_conn = {
            'host': 'your-hive-host',
            'port': 9083,
            'username': 'your-hive-username',
            'password': 'your-hive-password'
        }

        # Run the Hive query to extract data
        query = """
            SELECT 
                user_id,
                user_name
            FROM 
                logging_events
            WHERE 
                event_type = 'USER_CREATED'
        """

        # Execute the query and store the results in a list
        results = []
        # NOTE: You should implement the actual Hive query execution and result processing

        # Log the extracted data
        logging.info(f"Extracted {len(results)} user-created records")
        return results

    except Exception as e:
        # Log the exception and re-raise it to trigger a retry
        logging.error(f"Error extracting user-created data: {e}")
        raise

def transform_user_data(**kwargs):
    """
    Transform the extracted user-created data into the required format.
    """
    try:
        # Get the extracted data from the previous task
        extracted_data = kwargs['task_instance'].xcom_pull(task_ids='extract_users_created')

        # Transform the data into the required format
        transformed_data = []
        for record in extracted_data:
            transformed_record = {
                'user_id': record['user_id'],
                'user_name': record['user_name']
            }
            transformed_data.append(transformed_record)

        # Log the transformed data
        logging.info(f"Transformed {len(transformed_data)} user-created records")
        return transformed_data

    except Exception as e:
        # Log the exception and re-raise it to trigger a retry
        logging.error(f"Error transforming user-created data: {e}")
        raise

def load_user_data(**kwargs):
    """
    Load the transformed user-created data into the fct_users_created table.
    """
    try:
        # Get the transformed data from the previous task
        transformed_data = kwargs['task_instance'].xcom_pull(task_ids='transform_user_data')

        # Load the data into the fct_users_created table
        # NOTE: You should implement the actual data loading into the destination table

        # Log the loaded data
        logging.info(f"Loaded {len(transformed_data)} user-created records into fct_users_created")
        return True

    except Exception as e:
        # Log the exception and re-raise it to trigger a retry
        logging.error(f"Error loading user-created data: {e}")
        raise

with DAG(
    'fct_users_created_dag',
    default_args=default_args,
    description='A DAG to extract, transform, and load user-created data',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    tags=['user_created', 'fct_users_created'],
) as dag:
    extract_users_created_task = PythonOperator(
        task_id='extract_users_created',
        python_callable=extract_users_created,
        retries=3,
        retry_backoff_factor=5
    )

    transform_user_data_task = PythonOperator(
        task_id='transform_user_data',
        python_callable=transform_user_data,
        retries=3,
        retry_backoff_factor=5
    )

    load_user_data_task = PythonOperator(
        task_id='load_user_data',
        python_callable=load_user_data,
        retries=3,
        retry_backoff_factor=5
    )

    extract_users_created_task >> transform_user_data_task >> load_user_data_task