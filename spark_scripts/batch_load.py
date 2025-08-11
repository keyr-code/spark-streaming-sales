"""
Load data from Minio to postgres using Spark
"""

import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_timestamp, current_timestamp

# Add parent directory to path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from config import minio_config, postgres_config
from utils.logger.logger import setup_logger

logger = setup_logger(__name__)


def create_spark_session():
    """
    Create Spark session with MinIO and PostgreSQL configurations

    Returns:
        SparkSession: Configured Spark session
    """
    # Create Spark session
    spark = (
        SparkSession.builder.appName("TheGoods-Data-Processor")
        .config(
            "spark.jars.packages",
            "org.apache.hadoop:hadoop-aws:3.3.1,org.postgresql:postgresql:42.3.1",
        )
        .config(
            "spark.hadoop.fs.s3a.endpoint",
            f"http://{minio_config.MINIO_CONFIG['endpoint']}",
        )
        .config(
            "spark.hadoop.fs.s3a.access.key", minio_config.MINIO_CONFIG["access_key"]
        )
        .config(
            "spark.hadoop.fs.s3a.secret.key", minio_config.MINIO_CONFIG["secret_key"]
        )
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .getOrCreate()
    )

    # Set log level
    spark.sparkContext.setLogLevel("WARN")

    return spark


def read_from_minio(spark, bucket, object_name):
    """
    Read data from MinIO

    Args:
        spark (SparkSession): Spark session
        bucket (str): Bucket name
        object_name (str): Object name

    Returns:
        DataFrame: Spark DataFrame
    """
    folder_name = object_name.split(".")[0]  # Get name without extension
    path = f"s3a://{bucket}/{folder_name}/{object_name}"

    try:
        df = spark.read.option("header", "true").option("inferSchema", "true").csv(path)
        logger.info(f"Read {df.count()} records from {path}")
        return df
    except Exception as e:
        logger.error(f"Error reading from {path}: {str(e)}")
        return None


def write_to_postgres(df, table_name, spark, mode="append"):
    """
    Write DataFrame to PostgreSQL

    Args:
        df (DataFrame): Spark DataFrame
        table_name (str): Target table name
        spark (SparkSession): Spark session
        mode (str): Write mode ('overwrite', 'append', 'ignore', 'error')

    Returns:
        bool: True if successful
    """
    try:
        # Get PostgreSQL config
        pg_config = postgres_config.POSTGRES_CONFIG
        jdbc_url = f"jdbc:postgresql://{pg_config['host']}:{pg_config['port']}/{pg_config['database']}"

        # Write to PostgreSQL
        df.write.format("jdbc").option("url", jdbc_url).option(
            "dbtable", f"simzgoodz.{table_name}"
        ).option("user", pg_config["user"]).option(
            "password", pg_config["password"]
        ).option(
            "driver", "org.postgresql.Driver"
        ).mode(
            mode
        ).save()

        logger.info(f"Wrote data to PostgreSQL table: {table_name}")
        return True
    except Exception as e:
        logger.error(f"Error writing to PostgreSQL: {str(e)}")
        return False


def process_batch_data(spark):
    """
    Process batch data from MinIO and write to PostgreSQL

    Args:
        spark (SparkSession): Spark session

    Returns:
        bool: True if successful
    """
    try:
        # Get bucket name from config
        bucket_name = minio_config.MINIO_CONFIG["bucket"]
        logger.info(f"Reading data from bucket: {bucket_name}")

        # Read dimension tables
        logger.info("Reading dimension tables...")
        departments_df = read_from_minio(spark, bucket_name, "departments.csv")
        products_df = read_from_minio(spark, bucket_name, "products.csv")
        customers_df = read_from_minio(spark, bucket_name, "customers.csv")
        employees_df = read_from_minio(spark, bucket_name, "employees.csv")
        suppliers_df = read_from_minio(spark, bucket_name, "suppliers.csv")
        warehouses_df = read_from_minio(spark, bucket_name, "warehouses.csv")

        # Read fact tables
        logger.info("Reading fact tables...")
        sales_df = read_from_minio(spark, bucket_name, "sales.csv")
        sale_items_df = read_from_minio(spark, bucket_name, "sale_items.csv")
        inventory_trans_df = read_from_minio(
            spark, bucket_name, "inventory_transactions.csv"
        )

        # Transform sales data to fix duplicate sale_id issue
        if sales_df is not None:
            logger.info("Transforming sales data to fix duplicate sale_id issue...")
            # Check if we need to deduplicate sales data
            sales_count = sales_df.count()
            distinct_sales_count = sales_df.select("sale_id").distinct().count()

            if sales_count > distinct_sales_count:
                logger.info(
                    f"Found duplicate sale_id values: {sales_count} rows, {distinct_sales_count} unique sale_ids"
                )

                # Group by sale_id and aggregate
                from pyspark.sql import functions as F

                # Use proper aggregation functions for each column
                sales_df = sales_df.groupBy("sale_id").agg(
                    # For categorical fields, take the most common value
                    F.expr("approx_most_frequent(customer_id, 1)[0][0]").alias(
                        "customer_id"
                    ),
                    F.expr("approx_most_frequent(employee_id, 1)[0][0]").alias(
                        "employee_id"
                    ),
                    # For dates and times, take the earliest values
                    F.min("sale_date").alias("sale_date"),
                    F.min("sale_time").alias("sale_time"),
                    # For department, take the most common
                    F.expr("approx_most_frequent(dept_id, 1)[0][0]").alias("dept_id"),
                    # For monetary values, sum them
                    F.sum("subtotal").alias("subtotal"),
                    F.sum("tax").alias("tax"),
                    F.sum("total").alias("total"),
                    # For other categorical fields, take most common
                    F.expr("approx_most_frequent(payment_method, 1)[0][0]").alias(
                        "payment_method"
                    ),
                    F.expr("approx_most_frequent(store_id, 1)[0][0]").alias("store_id"),
                    F.expr("approx_most_frequent(register_id, 1)[0][0]").alias(
                        "register_id"
                    ),
                )

                # Count items for each sale
                if sale_items_df is not None:
                    items_count_df = sale_items_df.groupBy("sale_id").agg(
                        F.count("*").alias("items_count")
                    )
                    sales_df = sales_df.join(items_count_df, "sale_id", "left")

                logger.info(f"After deduplication: {sales_df.count()} unique sales")

        # Write dimension tables to PostgreSQL
        logger.info("Writing dimension tables to PostgreSQL...")
        if departments_df is not None:
            write_to_postgres(departments_df, "departments", spark)
        if products_df is not None:
            write_to_postgres(products_df, "products", spark)
        if customers_df is not None:
            write_to_postgres(customers_df, "customers", spark)
        if employees_df is not None:
            write_to_postgres(employees_df, "employees", spark)
        if suppliers_df is not None:
            write_to_postgres(suppliers_df, "suppliers", spark)
        if warehouses_df is not None:
            write_to_postgres(warehouses_df, "warehouses", spark)

        # Write fact tables to PostgreSQL
        logger.info("Writing fact tables to PostgreSQL...")
        if sales_df is not None:
            write_to_postgres(sales_df, "sales_fact", spark)

        if sale_items_df is not None:
            write_to_postgres(sale_items_df, "sales_items", spark)

        if inventory_trans_df is not None:
            write_to_postgres(inventory_trans_df, "inventory_transactions", spark)

        logger.info("Batch data processing complete")
        return True
    except Exception as e:
        logger.error(f"Error processing batch data: {str(e)}")
        return False


def main():
    """Main function"""
    # Create Spark session
    spark = create_spark_session()

    # Process batch data
    process_batch_data(spark)


if __name__ == "__main__":
    main()
