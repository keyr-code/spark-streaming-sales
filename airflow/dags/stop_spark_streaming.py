"""
Airflow DAG for stopping spark streaming processes
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'stop_spark_streaming',
    default_args=default_args,
    description='Stop Spark streaming job by restarting container',
    schedule_interval=None,
    start_date=datetime(2025, 1, 1),
    catchup=False
)

check_status = BashOperator(
    task_id='check_status',
    bash_command='''
    echo "Checking Spark container status..."
    docker ps | grep spark || echo "Spark container not running"
    ''',
    dag=dag
)

restart_spark = BashOperator(
    task_id='restart_spark',
    bash_command='''
    echo "Restarting Spark container to stop streaming job..."
    docker restart spark
    sleep 10
    
    # Clean up PID file if exists
    PID_FILE="/opt/airflow/dags/spark_live_streaming.pid"
    [ -f "$PID_FILE" ] && rm "$PID_FILE"
    
    echo "Spark container restarted successfully"
    ''',
    dag=dag
)

check_status >> restart_spark
