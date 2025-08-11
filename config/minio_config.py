"""
MinIO configuration settings for the music streaming application.
"""

# Default MinIO configuration
MINIO_CONFIG = {
    'endpoint': 'minio:9000',  # Use internal port 9000, not the host-mapped port
    'access_key': 'minioadmin',
    'secret_key': 'minioadmin',
    'secure': False,
    'bucket': 'simzgoodz'
}