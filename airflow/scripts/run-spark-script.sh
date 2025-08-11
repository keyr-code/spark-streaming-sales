#!/bin/bash

# Check if script name is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <script_path> [args...]"
  echo "Example: $0 spark/batch_load.py"
  exit 1
fi

SCRIPT_PATH=$1
shift  # Remove the first argument (script path)

# Run the Spark job in the Spark container 
docker exec spark sh -c "spark-submit --master local[*] /app/$SCRIPT_PATH \"$@\""
