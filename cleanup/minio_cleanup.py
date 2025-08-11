#!/usr/bin/env python3
"""
Script to empty a MinIO bucket
"""
import sys
import os
import logging

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from minio import Minio
from minio.error import S3Error
from config import minio_config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("minio_cleanup")

def empty_bucket(bucket_name):
    """
    Empty a MinIO bucket by deleting all objects
    
    Args:
        bucket_name (str): Name of the bucket to empty
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Initialize MinIO client
        client = Minio(
            minio_config.MINIO_CONFIG['endpoint'],
            access_key=minio_config.MINIO_CONFIG['access_key'],
            secret_key=minio_config.MINIO_CONFIG['secret_key'],
            secure=False
        )
        
        # Check if bucket exists
        if not client.bucket_exists(bucket_name):
            logger.warning(f"Bucket '{bucket_name}' does not exist")
            return True
        
        # List and delete all objects in the bucket
        objects = client.list_objects(bucket_name, recursive=True)
        object_count = 0
        
        for obj in objects:
            client.remove_object(bucket_name, obj.object_name)
            object_count += 1
            if object_count % 100 == 0:
                logger.info(f"Deleted {object_count} objects so far")
        
        logger.info(f"Successfully emptied bucket '{bucket_name}'. Deleted {object_count} objects.")
        return True
    
    except S3Error as e:
        logger.error(f"Error emptying bucket '{bucket_name}': {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False

def main():
    """Main function"""
    bucket_name = minio_config.MINIO_CONFIG['bucket']
    logger.info(f"Starting cleanup of MinIO bucket: {bucket_name}")
    
    success = empty_bucket(bucket_name)
    
    if success:
        logger.info("Cleanup completed successfully")
        return 0
    else:
        logger.error("Cleanup failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())