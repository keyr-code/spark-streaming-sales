"""
Airflow DAG for batch data processing
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

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
    'SimzGoodz_batch_processing',
    default_args=default_args,
    description='Process SimzGoodz department store batch data',
    schedule_interval=None,
    start_date=datetime(2025, 1, 1),
    catchup=False
)

# Task 1: Trigger cleanup DAG first
trigger_cleanup = TriggerDagRunOperator(
    task_id='trigger_cleanup_dag',
    trigger_dag_id='SimzGoodz_cleanup',
    wait_for_completion=True,
    dag=dag
)

# Task 2: Create PostgreSQL tables
# Read SQL file directly instead of relying on Jinja templating
with open('/opt/airflow/sql/ddl/create_tables.sql', 'r') as f:
    create_tables_sql = f.read()

create_tables = PostgresOperator(
    task_id='create_postgres_tables',
    postgres_conn_id='postgres_default',
    sql=create_tables_sql,
    dag=dag
)

# Task 2: Upload data to MinIO using Docker container
upload_data = BashOperator(
    task_id='upload_data_to_minio',
    bash_command='/opt/airflow/scripts/run-python-script.sh extract/upload_to_minio.py',
    dag=dag
)

# Task 3: Process data with Spark
process_data = BashOperator(
    task_id='process_data_with_spark',
    bash_command='/opt/airflow/scripts/run-spark-script.sh spark_scripts/batch_load.py',
    dag=dag
)


# Task 5: Ensure primary keys are properly defined
with open('/opt/airflow/sql/ddl/add_primary_keys.sql', 'r') as f:
    add_primary_keys_sql = f.read()

add_primary_keys = PostgresOperator(
    task_id='add_primary_keys',
    postgres_conn_id='postgres_default',
    sql=add_primary_keys_sql,
    dag=dag
)

# Task 6: Add foreign keys for Postgres tables
# Read SQL file directly
with open('/opt/airflow/sql/ddl/add_foreign_keys.sql', 'r') as f:
    add_foreign_keys_sql = f.read()

add_foreign_key = PostgresOperator(
    task_id='add_foreign_keys',
    postgres_conn_id='postgres_default',
    sql=add_foreign_keys_sql,
    dag=dag
)

# Set task dependencies
trigger_cleanup >> create_tables >> upload_data >> process_data >> add_primary_keys >> add_foreign_key