"""
Kafka producer for SimzGoodz department store sales data
"""

import argparse
import json
import socket
import time
import sys
import os

# Add the parent directory to the Python path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from confluent_kafka import Producer
from generate.create_sales_data import SalesDataStreamGenerator
from config import kafka_config
from utils.logger.logger import setup_logger

# Initialize logger
logger = setup_logger("kafka_producer")
logger.info("Kafka Producer logger initialized.")


def delivery_report(err, msg):
    """Callback for message delivery reports"""
    if err is not None:
        logger.error(f"Message delivery failed: {err}")
    else:
        logger.debug(
            f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}"
        )


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Stream Sales data to Kafka")

    # Data format parameter
    parser.add_argument(
        "-b",
        "--batch_size",
        type=int,
        default=10,
        help="Number of records to generate in each batch",
    )
    parser.add_argument(
        "-i",
        "--interval",
        type=float,
        default=1.0,
        help="Time interval between batches in seconds",
    )

    # Kafka specific parameters
    parser.add_argument(
        "--bootstrap-servers",
        default=kafka_config.PRODUCER_CONFIG["bootstrap.servers"],
        help="Kafka bootstrap servers",
    )
    parser.add_argument(
        "-t",
        "--topic",
        default=kafka_config.PRODUCER_CONFIG["topic"],
        help="Kafka topic to produce to",
    )

    args = parser.parse_args()

    # Create data generator
    generator = SalesDataStreamGenerator()

    # Configure Kafka producer
    conf = {
        "bootstrap.servers": args.bootstrap_servers,
        "client.id": socket.gethostname(),
    }

    producer = Producer(conf)

    logger.info(f"Starting Kafka producer, sending to topic {args.topic}...")
    logger.info(f"Batch size: {args.batch_size}, Interval: {args.interval} seconds")

    try:
        record_count = 0
        while True:
            # Generate a batch of records
            batch_records = []
            for _ in range(args.batch_size):
                record = generator.generate_sale()
                batch_records.append(record)
                record_count += 1
                data = json.dumps(record)
                producer.produce(
                    args.topic, data.encode("utf-8"), callback=delivery_report
                )

            # Flush producer queue after each batch
            producer.flush()
            logger.info(
                f"Sent batch of {args.batch_size} records. Total: {record_count}"
            )
            # Wait for the specified interval
            time.sleep(args.interval)

    except KeyboardInterrupt:
        logger.info(f"Streaming stopped. Total records sent: {record_count}")
        # Flush any remaining messages
        producer.flush()


if __name__ == "__main__":
    main()
