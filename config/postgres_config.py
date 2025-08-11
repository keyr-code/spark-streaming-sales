"""
PostgreSQL configuration settings for the music streaming application.
"""

# PostgreSQL connection configuration
POSTGRES_CONFIG = {
    "host": "pgdatabase",  # Use container name instead of localhost
    "port": 5432,
    "database": "goods_store",  # Match the database name in docker-compose.yaml
    "user": "root",
    "password": "root",
}
