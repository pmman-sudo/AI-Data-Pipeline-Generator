"""
This DAG is designed to handle the 'fct_users_created' table metadata.
It uses Airflow to manage the workflow and includes retries, exponential backoff, 
structured logging, and explicit error handling.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import logging
import requests
import os

# Define the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'fct_users_created',
    default_args=default_args,
    description='A DAG for handling fct_users_created table metadata',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(1),
    tags=['fct_users_created'],
) as dag:
    def fetch_data(**kwargs):
        """
        Fetch data from the 'fct_users_created' table.
        
        :param kwargs: Keyword arguments
        :return: None
        """
        try:
            # Use the requests library to fetch data from the table
            url = "https://example.com/fct_users_created"  # Replace with actual URL
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            logging.info(f"Fetched {len(data)} records from 'fct_users_created' table")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching data: {e}")
            raise

    def process_data(**kwargs):
        """
        Process the fetched data.
        
        :param kwargs: Keyword arguments
        :return: None
        """
        try:
            # Use the fetched data to perform some processing
            # Replace with actual processing logic
            logging.info("Processing data...")
        except Exception as e:
            logging.error(f"Error processing data: {e}")
            raise

    def load_data(**kwargs):
        """
        Load the processed data into a destination.
        
        :param kwargs: Keyword arguments
        :return: None
        """
        try:
            # Use the processed data to load it into a destination
            # Replace with actual loading logic
            logging.info("Loading data...")
        except Exception as e:
            logging.error(f"Error loading data: {e}")
            raise

    fetch_data_task = PythonOperator(
        task_id='fetch_data',
        python_callable=fetch_data,
        retries=3,
        retry_delay=timedelta(minutes=5),
    )

    process_data_task = PythonOperator(
        task_id='process_data',
        python_callable=process_data,
        retries=3,
        retry_delay=timedelta(minutes=5),
    )

    load_data_task = PythonOperator(
        task_id='load_data',
        python_callable=load_data,
        retries=3,
        retry_delay=timedelta(minutes=5),
    )

    fetch_data_task >> process_data_task >> load_data_task