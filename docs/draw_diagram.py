"""
Generate architecture diagram using Python
Install: pip install diagrams
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.storage import S3
from diagrams.aws.database import RDS
from diagrams.aws.analytics import KinesisDataStreams
from diagrams.onprem.workflow import Airflow
from diagrams.onprem.analytics import Spark

with Diagram("SimzGoodz Data Pipeline", show=False, direction="TB"):
    airflow = Airflow("Airflow\nOrchestrator")

    with Cluster("Batch Processing"):
        csv = S3("CSV Files")
        minio_batch = S3("MinIO")
        spark_batch = Spark("Spark Batch")
        postgres_batch = RDS("PostgreSQL")

        csv >> minio_batch >> spark_batch >> postgres_batch

    with Cluster("Stream Processing"):
        kafka = KinesisDataStreams("Kafka")
        spark_stream = Spark("Spark Streaming")
        postgres_stream = RDS("PostgreSQL")
        minio_backup = S3("MinIO Backup")

        kafka >> spark_stream >> postgres_stream
        spark_stream >> minio_backup

    airflow >> Edge(label="orchestrates") >> [csv, kafka]
