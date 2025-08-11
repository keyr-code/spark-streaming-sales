"""
Upload data files to MinIO
"""
import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(project_root)

# Import modules
from config import minio_config
from utils.logger.logger import setup_logger
from minio import Minio
from minio.error import S3Error


# Initialize logger
logger = setup_logger(__name__)

# Get MinIO configuration from config file
MINIO_ENDPOINT = minio_config.MINIO_CONFIG['endpoint']
MINIO_ACCESS_KEY = minio_config.MINIO_CONFIG['access_key']
MINIO_SECRET_KEY = minio_config.MINIO_CONFIG['secret_key']
MINIO_SECURE = minio_config.MINIO_CONFIG.get('secure', False)

# Bucket names
RAW_DATA_BUCKET = minio_config.MINIO_CONFIG['bucket']

# Data path - use the mounted path in the container
DATA_PATH = "/app/data/raw"

def create_minio_client():
    """
    Create MinIO client
    
    Returns:
        Minio: MinIO client
    """
    return Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=MINIO_SECURE
    )

def ensure_bucket_exists(client, bucket_name):
    """
    Ensure bucket exists, create if it doesn't
    
    Args:
        client (Minio): MinIO client
        bucket_name (str): Bucket name
    """
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
        logger.info(f"Created bucket: {bucket_name}")
    else:
        logger.info(f"Bucket already exists: {bucket_name}")

def upload_file(client, bucket_name, file_path, object_name=None):
    """
    Upload file to MinIO
    
    Args:
        client (Minio): MinIO client
        bucket_name (str): Bucket name
        file_path (str): Path to file
        object_name (str): Object name in MinIO (default: file basename)
        
    Returns:
        bool: True if successful
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return False
        
    if object_name is None:
        object_name = os.path.basename(file_path)
        
    try:
        client.fput_object(
            bucket_name,
            object_name,
            file_path,
            content_type="application/csv"
        )
        logger.info(f"Uploaded {file_path} to {bucket_name}/{object_name}")
        return True
    except S3Error as e:
        logger.error(f"Error uploading {file_path}: {e}")
        return False

def upload_directory(client, bucket_name, directory_path):
    """
    Upload all files in directory to MinIO, creating a folder for each file
    
    Args:
        client (Minio): MinIO client
        bucket_name (str): Bucket name
        directory_path (str): Path to directory
        
    Returns:
        int: Number of files uploaded
    """
    if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
        logger.error(f"Directory not found: {directory_path}")
        return 0
        
    count = 0
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        
        if os.path.isfile(file_path) and filename.endswith('.csv'):
            # Create folder name from filename without extension
            folder_name = os.path.splitext(filename)[0]
            # Set object name to include folder
            object_name = f"{folder_name}/{filename}"
            
            if upload_file(client, bucket_name, file_path, object_name):
                count += 1
                
    logger.info(f"Uploaded {count} files from {directory_path} to {bucket_name}")
    return count


def main():
    """Main function"""
    try:
        # Create MinIO client
        client = create_minio_client()
        
        # Ensure bucket exists
        ensure_bucket_exists(client, RAW_DATA_BUCKET)
        
        # Upload data files
        upload_directory(client, RAW_DATA_BUCKET, DATA_PATH)
        
        logger.info("Data upload complete")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()