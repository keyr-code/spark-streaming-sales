"""
Airflow DAG for live streaming data processing
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
import time

# Default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=5)
}

# DAG definition
dag = DAG(
    'SimzGoodz_live_streaming',
    default_args=default_args,
    description='Process SimzGoodz department store streaming data',
    schedule_interval=None,
    start_date=datetime(2025, 1, 1),
    catchup=False
)


# Task 1: Start Kafka producer
start_kafka_producer = BashOperator(
    task_id='start_kafka_producer',
    bash_command='/opt/airflow/scripts/run-python-script.sh kafka/kafka_producer.py',
    dag=dag
)

# Task 2: Start Spark streaming
start_streaming = BashOperator(
    task_id='start_streaming',
    bash_command='/opt/airflow/scripts/run-spark-script.sh spark_scripts/live_streaming.py',
    dag=dag
)


# Set task dependencies
[start_kafka_producer, start_streaming]