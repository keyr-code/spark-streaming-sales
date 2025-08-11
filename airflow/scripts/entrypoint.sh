#!/bin/bash
set -e

if [ -e "/opt/airflow/requirements.txt" ]; then
  $(command -v pip) install -r requirements.txt --constraint constraints-3.11.txt
fi

# Remove stale PID file if it exists
if [ -f /opt/airflow/airflow-webserver.pid ]; then
  rm /opt/airflow/airflow-webserver.pid
  echo "Removed stale PID file"
fi

if [ ! -f "/opt/airflow/airflow.db" ]; then
  airflow db init && \
  airflow users create \
    --username admin \
    --firstname admin \
    --lastname admin \
    --role Admin \
    --email admin@example.com \
    --password admin
fi

$(command -v airflow) db upgrade

# Create postgres_default connection
airflow connections delete postgres_default || true
airflow connections add postgres_default \
  --conn-type postgres \
  --conn-host pgdatabase \
  --conn-login root \
  --conn-password root \
  --conn-schema goods_store \
  --conn-port 5432

# Make run scripts executable
chmod +x /opt/airflow/scripts/run-python-script.sh
chmod +x /opt/airflow/scripts/run-spark-script.sh

# Start the scheduler in the background
airflow scheduler &

# Start the webserver
exec airflow webserver