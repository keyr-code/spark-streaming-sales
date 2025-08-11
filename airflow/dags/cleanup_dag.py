"""
Airflow DAG for cleaning up data
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator

# Default arguments
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# DAG definition
dag = DAG(
    "SimzGoodz_cleanup",
    default_args=default_args,
    description="Clean up MinIO bucket and drop PostgreSQL tables",
    schedule_interval=None,  # Manual trigger only
    start_date=datetime(2023, 1, 1),
    catchup=False,
)

# Task 1: Empty MinIO bucket
empty_minio = BashOperator(
    task_id="empty_minio_bucket",
    bash_command="/opt/airflow/scripts/run-python-script.sh cleanup/minio_cleanup.py",
    dag=dag,
)

# Task 2: Drop PostgreSQL tables
# Read SQL file directly
with open("/opt/airflow/sql/ddl/drop_tables.sql", "r") as f:
    drop_tables_sql = f.read()

drop_tables = PostgresOperator(
    task_id="drop_postgres_tables",
    postgres_conn_id="postgres_default",
    sql=drop_tables_sql,
    dag=dag,
)

# Set task dependencies
empty_minio >> drop_tables
