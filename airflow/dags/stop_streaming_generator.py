"""
Airflow DAG for stopping sales producer
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "stop_streaming_generator",
    default_args=default_args,
    description="Stop SimzGoodz sales producer",
    schedule_interval=None,
    start_date=datetime(2025, 1, 1),
    catchup=False,
)

stop_producer = BashOperator(
    task_id="stop_producer",
    bash_command="docker exec python pkill -f kafka_producer.py || true",
    dag=dag,
)

stop_producer
