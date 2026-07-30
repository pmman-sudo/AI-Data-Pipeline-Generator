from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator

default_args = {
    'owner': 'jdoe',
    'depends_on_past': False,
    'start_date': datetime(2023, 12, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'fct_users_created',
    default_args=default_args,
    schedule_interval=timedelta(days=1),
)

def extract_logging_events(**kwargs):
    from pyhive import hive
    from thrift import Thrift
    from thrift.transport import TTransport
    from thrift.protocol import TBinaryProtocol

    transport = TTransport.TBufferedTransport(hive.connect(host='hive-host', port=9083).transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = hive.Client(protocol)

    query = """
        SELECT 
            user_id, 
            user_name 
        FROM 
            logging_events
    """
    client.execute(query)
    results = client.fetchAll()
    return results

def load_fct_users_created(**kwargs):
    from pyhive import hive
    from thrift import Thrift
    from thrift.transport import TTransport
    from thrift.protocol import TBinaryProtocol

    transport = TTransport.TBufferedTransport(hive.connect(host='hive-host', port=9083).transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = hive.Client(protocol)

    results = kwargs['task_instance'].xcom_pull(task_ids='extract_logging_events')
    client.execute("CREATE TABLE IF NOT EXISTS fct_users_created (user_id varchar(100), user_name boolean)")
    for row in results:
        query = """
            INSERT INTO fct_users_created (user_id, user_name) 
            VALUES ('{}', {})
        """.format(row[0], row[1])
        client.execute(query)

extract_logging_events_task = PythonOperator(
    task_id='extract_logging_events',
    python_callable=extract_logging_events,
    dag=dag,
)

load_fct_users_created_task = PythonOperator(
    task_id='load_fct_users_created',
    python_callable=load_fct_users_created,
    dag=dag,
)

end_task = BashOperator(
    task_id='end_task',
    bash_command='echo "DAG finished)',
    dag=dag,
)

extract_logging_events_task >> load_fct_users_created_task >> end_task