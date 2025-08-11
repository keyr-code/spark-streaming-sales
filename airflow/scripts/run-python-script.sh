#!/bin/bash

# Check if script path is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <script_path> [args...]"
    echo "Example: $0 extract/upload_to_minio.py"
    exit 1
fi

SCRIPT_PATH=$1
shift  # Remove the first argument (script path)

# Run the script in the container
echo "Running $SCRIPT_PATH in Python container..."
docker exec python python /app/$SCRIPT_PATH "$@"
