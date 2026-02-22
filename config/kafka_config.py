"""
Kafka configuration settings for the music streaming application.
"""

# Default Kafka configuration
DEFAULT_CONFIG = {
    "bootstrap.servers": "broker:29092",  # Use broker:29092 for Docker container communication
    "topic": "sales-events",
}

# Producer specific configuration
PRODUCER_CONFIG = {
    **DEFAULT_CONFIG,
    "batch.size": 16384,
    "linger.ms": 1,
    "acks": "all",
    "topic": "sales-events",
}

# Consumer specific configuration
CONSUMER_CONFIG = {
    **DEFAULT_CONFIG,
    "group.id": "sales-events",
    "auto.offset.reset": "earliest",
    "enable.auto.commit": True,
}
