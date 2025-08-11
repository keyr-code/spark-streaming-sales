import os
import sys
import datetime
import time
# Add parent directory to Python path to find the config module
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_timestamp, current_timestamp, explode
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType, ArrayType
from config import minio_config, postgres_config
import logging

import signal
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("spark_streaming")

# Global variables for batch accumulation
accumulated_records = []
BATCH_SIZE = 1000  # Number of records to accumulate before saving to MinIO
last_record_time = time.time()
NO_DATA_TIMEOUT = 120  # 2 minutes in seconds


# Add at top of file
shutdown_flag = threading.Event()

def signal_handler(signum, frame):
    shutdown_flag.set()

def create_spark_session():
    """
    Create and configure a Spark session
    
    Returns:
        SparkSession: Configured Spark session
    """
    spark = (SparkSession.builder
        .appName("TheGoods-Streaming-Processor")
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.1,org.postgresql:postgresql:42.3.1,org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0")
        .config("spark.hadoop.fs.s3a.endpoint", f"http://{minio_config.MINIO_CONFIG['endpoint']}")
        .config("spark.hadoop.fs.s3a.access.key", minio_config.MINIO_CONFIG['access_key'])
        .config("spark.hadoop.fs.s3a.secret.key", minio_config.MINIO_CONFIG['secret_key'])
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .getOrCreate())
    
    # Set log level
    spark.sparkContext.setLogLevel("info")
    return spark


def write_to_postgres(df, table_name, mode="append"):
    """
    Write DataFrame to PostgreSQL
    
    Args:
        df (DataFrame): Spark DataFrame
        table_name (str): Target table name
        mode (str): Write mode ('overwrite', 'append', 'ignore', 'error')
        
    Returns:
        bool: True if successful
    """
    try:
        # Get PostgreSQL config
        pg_config = postgres_config.POSTGRES_CONFIG
        jdbc_url = f"jdbc:postgresql://{pg_config['host']}:{pg_config['port']}/{pg_config['database']}"
        
        # Write to PostgreSQL
        df.write \
            .format("jdbc") \
            .option("url", jdbc_url) \
            .option("dbtable", f"simzgoodz.{table_name}") \
            .option("user", pg_config['user']) \
            .option("password", pg_config['password']) \
            .option("driver", "org.postgresql.Driver") \
            .mode("ignore") \
            .save()
            
        logger.info(f"Wrote data to PostgreSQL table: {table_name}")
        return True
    except Exception as e:
        logger.error(f"Error writing to PostgreSQL: {str(e)}")
        return False


def save_accumulated_to_minio(spark, bucket, path_prefix):
    """
    Save accumulated records to MinIO in JSON format
    
    Args:
        spark (SparkSession): Spark session
        bucket (str): MinIO bucket name
        path_prefix (str): Path prefix for the output files
        
    Returns:
        bool: True if successful
    """
    global accumulated_records
    if not accumulated_records:
        return True  # Nothing to save
    
    try:
        # Generate a timestamp-based path
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        path = f"s3a://{bucket}/{path_prefix}/{timestamp}"
        
        # Convert accumulated records to DataFrame
        df = spark.createDataFrame(accumulated_records)
        
        # Save as JSON
        df.write.json(path)
        
        # Clear accumulated records
        record_count = len(accumulated_records)
        accumulated_records = []
        
        logger.info(f"Saved {record_count} accumulated records to {path}")
        return True
    except Exception as e:
        logger.error(f"Error saving accumulated records to MinIO: {str(e)}")
        return False


def process_batch(df, epoch_id):
    """
    Process each batch of streaming data
    
    Args:
        df (DataFrame): Batch DataFrame
        epoch_id (int): Epoch ID
    """
    global last_record_time
    
    if df.isEmpty():
        logger.info(f"Empty batch received at epoch {epoch_id}")
        if time.time() - last_record_time > NO_DATA_TIMEOUT:
            logger.info("No data received for 2 minutes. Stopping stream...")
            cleanup_resources()
            df.sparkSession.streams.active[0].stop()
        return
    
    # Update last record time when data is received
    last_record_time = time.time()
    
    try:
        # Print schema to debug
        logger.info(f"DataFrame schema: {df.schema}")
        
        # Register the DataFrame as a temporary view
        df.createOrReplaceTempView("sales_stream")
        
        # Accumulate records for MinIO backup
        new_records = df.collect()
        accumulated_records.extend(new_records)
        logger.info(f"Accumulated {len(new_records)} records, total: {len(accumulated_records)}")
        
        # Save to MinIO if we've reached the batch size
        bucket_name = minio_config.MINIO_CONFIG['bucket']
        if len(accumulated_records) >= BATCH_SIZE:
            save_accumulated_to_minio(df.sparkSession, bucket_name, "raw_sales_backup")
        
        # Process sales_fact data
        sales_fact_df = df
        
        # Add date column and convert time column
        sales_fact_df = sales_fact_df \
            .withColumn("sale_date", to_timestamp(col("sale_time")).cast("date")) \
            .withColumn("sale_time", to_timestamp(col("sale_time"))) \
            .select(
                "sale_id", "customer_id", "employee_id", "sale_date", "sale_time", "dept_id",
                "subtotal", "tax", "total", "payment_method",
                "store_id", "register_id", "items_count"
            )
        
        # Process sales_items data - explode the items array
        items_df = df.select("sale_id", explode("items").alias("item"))
        sales_items_df = items_df.select(
            "sale_id",
            col("item.product_id").alias("product_id"),
            col("item.quantity").alias("quantity"),
            col("item.unit_price").alias("unit_price"),
            col("item.discount_percent").alias("discount_percent"),
            col("item.item_total").alias("item_total")
        )
        
        # Write to PostgreSQL
        logger.info(f"Writing {sales_fact_df.count()} records to sales_fact table")
        write_to_postgres(sales_fact_df, "sales_fact")
        
        logger.info(f"Writing {sales_items_df.count()} records to sales_items table")
        write_to_postgres(sales_items_df, "sales_items")
        
        logger.info(f"Successfully processed batch at epoch {epoch_id}")
    except Exception as e:
        logger.error(f"Error processing batch at epoch {epoch_id}: {str(e)}")


def process_streaming_data(spark):
    """
    Process streaming data from Kafka and write to PostgreSQL
    
    Args:
        spark (SparkSession): Spark session
        
    Returns:
        StreamingQuery: Spark streaming query
    """
    try:
        # Define schema for sales data
        sales_schema = StructType([
            StructField("sale_id", StringType(), False),
            StructField("customer_id", StringType(), False),
            StructField("employee_id", StringType(), False),
            StructField("sale_time", StringType(), False),
            StructField("dept_id", IntegerType(), False),
            StructField("subtotal", DoubleType(), False),
            StructField("tax", DoubleType(), False),
            StructField("total", DoubleType(), False),
            StructField("payment_method", StringType(), False),
            StructField("store_id", StringType(), False),
            StructField("register_id", StringType(), False),
            StructField("items_count", IntegerType(), False),
            StructField("items", ArrayType(StructType([
                StructField("product_id", StringType(), False),
                StructField("quantity", IntegerType(), False),
                StructField("unit_price", DoubleType(), False),
                StructField("discount_percent", DoubleType(), True),
                StructField("item_total", DoubleType(), False)
            ])), False)
        ])
        
        # Read from Kafka
        kafka_df = spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", "broker:29092") \
            .option("subscribe", "sales-events") \
            .option("startingOffsets", "earliest") \
            .load()
            
        # Parse JSON data
        parsed_df = kafka_df \
            .selectExpr("CAST(value AS STRING) as json") \
            .select(from_json("json", sales_schema).alias("data")) \
            .select("data.*")
        
        # Process each batch
        
        checkpoint_dir = "/tmp/checkpoints_sales_events"
        query = parsed_df.writeStream \
            .foreachBatch(process_batch) \
            .outputMode("append") \
            .option("checkpointLocation", checkpoint_dir) \
            .start()
            
        logger.info("Started streaming data processing")
        return query
    except Exception as e:
        logger.error(f"Error processing streaming data: {str(e)}")
        raise


def cleanup_resources():
    """
    Clean up resources before shutdown
    """
    
    # Save any remaining accumulated records
    if accumulated_records:
        logger.info(f"Saving {len(accumulated_records)} remaining records before shutdown")
        bucket_name = minio_config.MINIO_CONFIG['bucket']
        save_accumulated_to_minio(spark, bucket_name, "raw_sales_backup")

# if __name__ == "__main__":
#     logger.info("Starting sales data streaming processor")
#     spark = create_spark_session()
#     query = process_streaming_data(spark)
    
#     try:
#         query.awaitTermination()
#     except KeyboardInterrupt:
#         logger.info("Received shutdown signal")
#     finally:
#         # Save any remaining records before shutdown
#         cleanup_resources()
#         spark.stop()
#         logger.info("Streaming application stopped")


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    spark = create_spark_session()
    query = process_streaming_data(spark)
    
    try:
        # Check shutdown flag every second instead of blocking indefinitely
        while query.isActive and not shutdown_flag.is_set():
            time.sleep(1)
        
        if shutdown_flag.is_set():
            query.stop()
            
    finally:
        cleanup_resources()
        spark.stop()